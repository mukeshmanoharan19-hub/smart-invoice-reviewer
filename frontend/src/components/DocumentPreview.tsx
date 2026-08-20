type Props = {
  file: File | null
  previewUrl: string | null
}

export function DocumentPreview({ file, previewUrl }: Props) {
  if (!file || !previewUrl) {
    return (
      <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
        Select a document to preview it here.
      </div>
    )
  }

  const isPdf = file.type === 'application/pdf'

  return (
    <div className="space-y-3">
      <div className="text-sm text-slate-600">
        <span className="font-medium text-slate-900">{file.name}</span>
        <span className="ml-2">({Math.round(file.size / 1024)} KB)</span>
      </div>
      {isPdf ? (
        <iframe title="Document preview" src={previewUrl} className="h-96 w-full rounded-lg border" />
      ) : (
        <img
          src={previewUrl}
          alt="Document preview"
          className="max-h-96 w-full rounded-lg border object-contain bg-white"
        />
      )}
    </div>
  )
}
