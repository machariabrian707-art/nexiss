import type { DocStatus } from '@/api/documents'

const MAP: Record<DocStatus, { label: string; cls: string }> = {
  uploaded:   { label: 'Uploaded',   cls: 'badge-gray' },
  processing: { label: 'Processing', cls: 'badge-yellow' },
  completed:  { label: 'Completed',  cls: 'badge-green' },
  failed:     { label: 'Failed',     cls: 'badge-red' },
}

export default function StatusBadge({ status }: { status: DocStatus | string }) {
  const cfg = MAP[status as DocStatus] ?? { label: status, cls: 'badge-gray' }
  return <span className={cfg.cls}>{cfg.label}</span>
}
