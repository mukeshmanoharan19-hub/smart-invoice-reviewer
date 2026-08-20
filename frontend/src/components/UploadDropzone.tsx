type Props = {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

const ACCEPT = 'application/pdf,image/png,image/jpeg'

export function UploadDropzone({ onFileSelected, disabled = false }: Props) {
  return (
    <label
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center ${
        disabled ? 'opacity-60' : 'hover:border-slate-400'
      }`}
    >
      <span className="text-base font-medium text-slate-900">Upload an invoice or receipt</span>
      <span className="mt-2 text-sm text-slate-600">
        PDF, PNG, or JPEG up to 4 MB. One document per review.
      </span>
      <input
        type="file"
        accept={ACCEPT}
        className="hidden"
        disabled={disabled}
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (file) {
            onFileSelected(file)
          }
          event.target.value = ''
        }}
      />
    </label>
  )
}
