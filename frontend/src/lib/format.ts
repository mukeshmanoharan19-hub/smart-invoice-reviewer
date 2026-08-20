export function formatMoney(amount: string | null, currency: string | null): string {
  if (amount === null || amount === '') {
    return '—'
  }
  return currency ? `${currency} ${amount}` : amount
}

export function formatDate(value: string | null): string {
  if (!value) {
    return '—'
  }
  return value
}

export function formatConfidence(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return '—'
  }
  return `${(value * 100).toFixed(0)}%`
}

export function emptyToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed.length === 0 ? null : trimmed
}
