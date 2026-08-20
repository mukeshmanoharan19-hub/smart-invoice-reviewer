import { Button } from './ui/Button'

type Props = {
  disabled?: boolean
  canApprove: boolean
  canDraftEmail?: boolean
  onApprove: () => void
  onReject: () => void
  onDraftEmail: () => void
}

export function DecisionBar({
  disabled = false,
  canApprove,
  canDraftEmail = false,
  onApprove,
  onReject,
  onDraftEmail,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      <Button onClick={onApprove} disabled={disabled || !canApprove}>
        Approve
      </Button>
      <Button variant="danger" onClick={onReject} disabled={disabled}>
        Reject
      </Button>
      <Button
        variant="secondary"
        onClick={onDraftEmail}
        disabled={disabled || !canDraftEmail}
      >
        Draft correction email
      </Button>
    </div>
  )
}
