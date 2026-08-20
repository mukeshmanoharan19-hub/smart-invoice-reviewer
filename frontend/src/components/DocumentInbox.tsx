import { ReviewHistory } from './ReviewHistory'
import { Panel } from './ui/Panel'
import type { ReviewSummary } from '../lib/types'

type Props = {
  reviews: ReviewSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

export function DocumentInbox({ reviews, selectedId, onSelect, onDelete }: Props) {
  return (
    <Panel>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Document inbox
      </h2>
      <p className="mt-1 text-xs text-slate-500">Newest reviews first. Delete to reset a demo.</p>
      <div className="mt-4">
        <ReviewHistory
          reviews={reviews}
          selectedId={selectedId}
          onSelect={onSelect}
          onDelete={onDelete}
        />
      </div>
    </Panel>
  )
}
