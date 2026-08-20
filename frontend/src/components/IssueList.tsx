import type { Issue } from '../lib/types'

type Props = {
  issues: Issue[]
}

export function IssueList({ issues }: Props) {
  if (issues.length === 0) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        No policy issues. Ready for Maya&apos;s decision once a GL account is selected.
      </div>
    )
  }

  return (
    <ul className="space-y-2">
      {issues.map((issue) => (
        <li
          key={`${issue.code}-${issue.field ?? 'none'}`}
          className={`rounded-lg border px-4 py-3 text-sm ${
            issue.severity === 'error'
              ? 'border-rose-200 bg-rose-50 text-rose-900'
              : 'border-amber-200 bg-amber-50 text-amber-900'
          }`}
        >
          <div className="font-medium uppercase tracking-wide">{issue.severity}</div>
          <div className="mt-1">{issue.message}</div>
          <div className="mt-1 text-xs opacity-80">{issue.code}</div>
        </li>
      ))}
    </ul>
  )
}
