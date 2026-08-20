import { DocumentPreview } from './DocumentPreview'
import { Button } from './ui/Button'
import { Panel } from './ui/Panel'

type Props = {
  file: File | null
  previewUrl: string | null
  busy?: boolean
  onProcess: () => void
  onChooseAnother: () => void
}

export function UploadStep({
  file,
  previewUrl,
  busy = false,
  onProcess,
  onChooseAnother,
}: Props) {
  return (
    <Panel>
      <h2 className="text-xl font-semibold text-slate-900">Preview and process</h2>
      <p className="mt-1 text-sm text-slate-600">
        Confirm the document looks right, then run the pipeline through the API.
      </p>
      <div className="mt-4">
        <DocumentPreview file={file} previewUrl={previewUrl} />
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <Button onClick={onProcess} disabled={busy || !file}>
          Process document
        </Button>
        <Button variant="secondary" disabled={busy} onClick={onChooseAnother}>
          Choose another file
        </Button>
      </div>
    </Panel>
  )
}
