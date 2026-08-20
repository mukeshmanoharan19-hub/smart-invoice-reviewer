import { Button } from './ui/Button'
import type { CorrectionEmail } from '../lib/types'

type Props = {
  draft: CorrectionEmail | null
  onClose: () => void
}

export function CorrectionEmailDialog({ draft, onClose }: Props) {
  if (!draft) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-auto rounded-xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-900">Correction email draft</h2>
        <p className="mt-1 text-sm text-slate-600">
          The app never sends this email. Copy it if you want to use it outside the demo.
        </p>
        <div className="mt-4 space-y-3">
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-slate-500">Subject</div>
            <div className="mt-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
              {draft.subject}
            </div>
          </div>
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-slate-500">Body</div>
            <pre className="mt-1 whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
              {draft.body}
            </pre>
          </div>
        </div>
        <div className="mt-5 flex gap-3">
          <Button
            onClick={async () => {
              await navigator.clipboard.writeText(`${draft.subject}\n\n${draft.body}`)
            }}
          >
            Copy
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}
