import type { GLAccount } from '../lib/types'

type Props = {
  accounts: GLAccount[]
  value: string | null
  suggestionCode: string | null
  suggestionRationale: string | null
  disabled?: boolean
  onChange: (code: string) => void
}

export function GLAccountSelect({
  accounts,
  value,
  suggestionCode,
  suggestionRationale,
  disabled = false,
  onChange,
}: Props) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-slate-900">
        GL account
        <select
          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
          value={value ?? ''}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">Select an account</option>
          {accounts.map((account) => (
            <option key={account.code} value={account.code}>
              {account.code} — {account.name}
            </option>
          ))}
        </select>
      </label>
      {suggestionCode ? (
        <p className="text-sm text-slate-600">
          Suggested <span className="font-medium">{suggestionCode}</span>
          {suggestionRationale ? `: ${suggestionRationale}` : ''}
        </p>
      ) : null}
    </div>
  )
}
