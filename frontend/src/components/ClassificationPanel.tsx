import { formatConfidence } from '../lib/format'
import type { ReviewDetail } from '../lib/types'
import { Panel } from './ui/Panel'

type Props = {
  review: ReviewDetail
}

export function ClassificationPanel({ review }: Props) {
  const classification = review.classification

  return (
    <Panel>
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Classification
      </h3>
      {classification ? (
        <div className="mt-3 space-y-2 text-sm text-slate-700">
          <p>
            Kind:{' '}
            <span className="font-medium text-slate-900">{classification.document_kind}</span>
            <span className="ml-3 text-slate-500">
              confidence {formatConfidence(classification.confidence)}
            </span>
          </p>
          <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-slate-700">
            {classification.reasoning}
          </p>
          <p className="text-xs text-slate-500">
            LLM confidence is a rough signal, not a calibrated probability. Reasoning is usually
            more useful for review.
          </p>
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">No classification payload stored for this review.</p>
      )}
    </Panel>
  )
}
