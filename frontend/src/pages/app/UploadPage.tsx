import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { documentsApi } from '@/api/documents'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'
import axios from 'axios'

const DOC_TYPES = [
  'Auto-detect',
  'Invoice', 'Receipt', 'Purchase Order', 'Bank Statement',
  'Financial Statement', 'Payroll Record', 'Tax Document',
  'Patient Record', 'Prescription', 'Lab Result', 'Medical Report',
  'Contract', 'Agreement', 'Legal Document',
  'Certificate', 'Transcript', 'Research Paper',
  'Employee Record', 'CV / Resume', 'Offer Letter',
  'Bill of Lading', 'Shipping Label', 'Customs Declaration',
  'National ID', 'Passport', 'Permit',
  'Handwritten Note', 'Scanned Document', 'Other',
]

interface FileState {
  file: File
  docTypeHint: string
  status: 'idle' | 'uploading' | 'done' | 'error'
  progress: number
  docId?: string
  error?: string
}

export default function UploadPage() {
  const navigate = useNavigate()
  const [files, setFiles] = useState<FileState[]>([])

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles: FileState[] = accepted.map((f) => ({
      file: f,
      docTypeHint: 'Auto-detect',
      status: 'idle',
      progress: 0,
    }))
    setFiles((prev) => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.tiff'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    maxSize: 50 * 1024 * 1024,
  })

  const removeFile = (idx: number) =>
    setFiles((prev) => prev.filter((_, i) => i !== idx))

  const updateHint = (idx: number, hint: string) =>
    setFiles((prev) => prev.map((f, i) => i === idx ? { ...f, docTypeHint: hint } : f))

  const uploadAll = async () => {
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'idle') continue
      setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, status: 'uploading', progress: 10 } : f))
      try {
        const { file, docTypeHint } = files[i]
        // 1. Get signed URL
        const { data: signed } = await documentsApi.signedUpload(file.name, file.type)
        setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, progress: 30 } : f))
        // 2. Upload to S3
        await axios.put(signed.upload_url, file, { headers: { 'Content-Type': file.type } })
        setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, progress: 60 } : f))
        // 3. Create document record
        const hint = docTypeHint === 'Auto-detect' ? undefined : docTypeHint
        const { data: doc } = await documentsApi.create({ s3_key: signed.s3_key, filename: file.name, doc_type_hint: hint })
        setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, progress: 80 } : f))
        // 4. Trigger processing
        await documentsApi.process(doc.id)
        setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, status: 'done', progress: 100, docId: doc.id } : f))
      } catch (err: unknown) {
        const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Upload failed'
        setFiles((prev) => prev.map((f, idx) => idx === i ? { ...f, status: 'error', error: msg } : f))
        toast.error(`Failed: ${files[i].file.name}`)
      }
    }
    toast.success('All files uploaded and queued for processing!')
  }

  const allDone = files.length > 0 && files.every((f) => f.status === 'done')

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
        <p className="text-sm text-gray-500 mt-1">
          Drop any document type — Nexiss will read, classify, and extract the data automatically.
        </p>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors',
          isDragActive ? 'border-brand-400 bg-brand-50' : 'border-gray-200 hover:border-brand-300 hover:bg-gray-50'
        )}
      >
        <input {...getInputProps()} />
        <Upload size={36} className={clsx('mx-auto mb-3', isDragActive ? 'text-brand-500' : 'text-gray-300')} />
        <p className="text-sm font-medium text-gray-700">
          {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to browse'}
        </p>
        <p className="text-xs text-gray-400 mt-1">PDF, Images (JPG/PNG), DOCX, XLSX, CSV, TXT — up to 50 MB each</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="card divide-y divide-gray-50">
          {files.map((fs, i) => (
            <div key={i} className="flex items-center gap-4 p-4">
              <FileText size={20} className="text-gray-400 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{fs.file.name}</p>
                <p className="text-xs text-gray-400">{(fs.file.size / 1024).toFixed(1)} KB</p>
                {/* Progress bar */}
                {fs.status === 'uploading' && (
                  <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-brand-500 rounded-full transition-all"
                      style={{ width: `${fs.progress}%` }}
                    />
                  </div>
                )}
                {fs.status === 'error' && <p className="text-xs text-red-500 mt-1">{fs.error}</p>}
              </div>

              {/* Doc type selector */}
              {fs.status === 'idle' && (
                <select
                  value={fs.docTypeHint}
                  onChange={(e) => updateHint(i, e.target.value)}
                  className="input w-44 text-xs"
                >
                  {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              )}

              {/* Status icon */}
              {fs.status === 'done' && <CheckCircle size={18} className="text-green-500 shrink-0" />}
              {fs.status === 'error' && <AlertCircle size={18} className="text-red-500 shrink-0" />}

              {/* Remove */}
              {fs.status === 'idle' && (
                <button onClick={() => removeFile(i)} className="text-gray-300 hover:text-gray-500">
                  <X size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      {files.length > 0 && (
        <div className="flex gap-3">
          {!allDone && (
            <button
              onClick={uploadAll}
              disabled={files.every((f) => f.status !== 'idle')}
              className="btn-primary"
            >
              <Upload size={15} />
              Upload & Process All
            </button>
          )}
          {allDone && (
            <button onClick={() => navigate('/app/documents')} className="btn-primary">
              View Documents
            </button>
          )}
          <button onClick={() => setFiles([])} className="btn-secondary">Clear</button>
        </div>
      )}
    </div>
  )
}
