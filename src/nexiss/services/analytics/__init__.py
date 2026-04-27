from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta, timezone

from nexiss.db.models.document import Document
from nexiss.db.models.usage_event import UsageEvent


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self, org_id: Optional[UUID] = None) -> dict:
        """Get document processing overview. If org_id is None, returns platform-wide stats."""
        base = select(Document)
        if org_id:
            base = base.where(Document.org_id == org_id)

        # Total
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))

        # By status
        for_status = base
        statuses = {}
        for s in ['completed', 'failed', 'processing', 'uploaded']:
            q = select(func.count()).select_from(
                for_status.where(Document.status == s).subquery()
            )
            statuses[s] = await self.db.scalar(q) or 0

        # Total pages
        pages_q = select(func.coalesce(func.sum(Document.page_count), 0))
        if org_id:
            pages_q = pages_q.where(Document.org_id == org_id)
        total_pages = await self.db.scalar(pages_q) or 0

        # Total LLM tokens (from usage events)
        tokens_q = select(func.coalesce(func.sum(UsageEvent.value), 0)).where(
            UsageEvent.metric_type == 'llm_tokens'
        )
        if org_id:
            tokens_q = tokens_q.where(UsageEvent.org_id == org_id)
        total_tokens = await self.db.scalar(tokens_q) or 0

        return {
            'total_documents': total or 0,
            'completed': statuses.get('completed', 0),
            'failed': statuses.get('failed', 0),
            'processing': statuses.get('processing', 0),
            'uploaded': statuses.get('uploaded', 0),
            'total_pages': int(total_pages),
            'total_llm_tokens': int(total_tokens),
        }

    async def get_daily_processing(self, days: int = 30, org_id: Optional[UUID] = None) -> list[dict]:
        """Daily document + page counts for the last N days."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        q = text("""
            SELECT
                DATE(created_at AT TIME ZONE 'UTC') AS date,
                COUNT(*) AS documents,
                COALESCE(SUM(page_count), 0) AS pages
            FROM documents
            WHERE created_at >= :since
              AND (:org_id IS NULL OR org_id = :org_id::uuid)
            GROUP BY DATE(created_at AT TIME ZONE 'UTC')
            ORDER BY date ASC
        """)

        result = await self.db.execute(q, {'since': since, 'org_id': str(org_id) if org_id else None})
        rows = result.fetchall()

        return [
            {'date': str(row.date), 'documents': row.documents, 'pages': int(row.pages)}
            for row in rows
        ]

    async def get_admin_stats(self) -> dict:
        """Platform-wide stats for super admin."""
        from nexiss.db.models.organization import Organization
        from nexiss.db.models.user import User

        total_orgs = await self.db.scalar(select(func.count(Organization.id)))
        total_users = await self.db.scalar(select(func.count(User.id)))
        total_docs = await self.db.scalar(select(func.count(Document.id)))
        failed_docs = await self.db.scalar(
            select(func.count(Document.id)).where(Document.status == 'failed')
        )
        processing_docs = await self.db.scalar(
            select(func.count(Document.id)).where(Document.status == 'processing')
        )

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        docs_today = await self.db.scalar(
            select(func.count(Document.id)).where(Document.created_at >= today_start)
        )

        return {
            'total_orgs': total_orgs or 0,
            'total_users': total_users or 0,
            'total_documents': total_docs or 0,
            'documents_today': docs_today or 0,
            'failed_documents': failed_docs or 0,
            'processing_queue': processing_docs or 0,
        }
