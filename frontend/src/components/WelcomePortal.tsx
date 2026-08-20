import { UploadDropzone } from './UploadDropzone'
import { Panel } from './ui/Panel'

type Props = {
  busy?: boolean
  onFileSelected: (file: File) => void
}

export function WelcomePortal({ busy = false, onFileSelected }: Props) {
  return (
    <Panel>
      <h2 className="text-xl font-semibold text-slate-900">Welcome, Maya</h2>
      <p className="mt-2 text-sm text-slate-600">
        Upload one multilingual invoice or receipt. The app classifies it, extracts fields with
        OpenAI, validates GSTIN and totals locally, suggests a GL account, and waits for your
        approval or rejection.
      </p>
      <div className="mt-6">
        <UploadDropzone onFileSelected={onFileSelected} disabled={busy} />
      </div>
    </Panel>
  )
}
