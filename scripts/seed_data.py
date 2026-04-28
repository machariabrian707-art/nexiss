import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from nexiss.db.session import AsyncSessionFactory
from nexiss.db.models.user import User
from nexiss.db.models.organization import Organization
from nexiss.db.models.org_membership import OrgMembership
from nexiss.core.security import get_password_hash

async def seed():
    async with AsyncSessionFactory() as session:
        # 1. Create Test Organization
        org_id = uuid.uuid4()
        org = Organization(
            org_id=org_id,
            name="Alpha Corp",
            slug="alpha-corp"
        )
        session.add(org)
        
        # 2. Create Super Admin
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            org_id=org_id,
            email="admin@nexiss.ai",
            password_hash=get_password_hash("nexiss2026"),
            full_name="Nexiss Administrator",
            is_superuser=True
        )
        session.add(user)
        
        # 3. Add to Organization
        membership = OrgMembership(
            org_id=org_id,
            user_id=user_id,
            role="admin"
        )
        session.add(membership)
        
        await session.commit()
        print(f"Seed complete!")
        print(f"Email: admin@nexiss.ai")
        print(f"Password: nexiss2026")
        print(f"Org ID: {org_id}")

if __name__ == "__main__":
    asyncio.run(seed())
