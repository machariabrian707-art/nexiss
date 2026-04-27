import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-700">
      <AlertCircle size={16} className="shrink-0" />
      {message}
    </div>
  )
}
