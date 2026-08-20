import { formatMoney } from '../lib/format'
import type { ReviewSummary } from '../lib/types'
import { Button } from './ui/Button'

type Props = {
  reviews: ReviewSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

export function ReviewHistory({ reviews, selectedId, onSelect, onDelete }: Props) {
  if (reviews.length === 0) {
    return <p className="text-sm text-slate-500">No reviews yet.</p>
  }

  return (
    <ul className="space-y-2">
      {reviews.map((review) => {
        const selected = review.id === selectedId
        return (
          <li
            key={review.id}
            className={`rounded-lg border px-3 py-3 ${
              selected ? 'border-slate-900 bg-slate-50' : 'border-slate-200 bg-white'
            }`}
          >
            <button
              type="button"
              className="w-full text-left"
              onClick={() => onSelect(review.id)}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-sm font-medium text-slate-900">{review.filename}</div>
                  <div className="mt-1 text-xs text-slate-600">
                    {review.document_type} · {review.status}
                  </div>
                  <div className="mt-1 text-xs text-slate-600">
                    {review.vendor_name ?? 'Unknown vendor'} ·{' '}
                    {formatMoney(review.total, review.currency)}
                  </div>
                </div>
              </div>
            </button>
            <div className="mt-2">
              <Button
                variant="ghost"
                className="px-0 text-rose-700"
                onClick={() => onDelete(review.id)}
              >
                Delete
              </Button>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
