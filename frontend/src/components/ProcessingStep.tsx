import { DocumentPreview } from './DocumentPreview'
import { Panel } from './ui/Panel'

type Props = {
  file: File | null
  previewUrl: string | null
}

export function ProcessingStep({ file, previewUrl }: Props) {
  return (
    <Panel>
      <h2 className="text-xl font-semibold text-slate-900">Processing document…</h2>
      <p className="mt-2 text-sm text-slate-600">
        Classification, extraction, GL suggestion, and validation are running on the backend. This
        is the same chain as the pipeline playground, triggered by your upload.
      </p>
      <div className="mt-4">
        <DocumentPreview file={file} previewUrl={previewUrl} />
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full w-1/2 animate-pulse rounded-full bg-slate-800" />
      </div>
    </Panel>
  )
}
