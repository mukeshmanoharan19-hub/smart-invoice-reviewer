import { env } from './env'
import type {
  CorrectionEmail,
  GLAccount,
  ReviewDetail,
  ReviewFields,
  ReviewSummary,
} from './types'

class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let message = `Request failed with status ${response.status}`
  try {
    const payload: unknown = await response.json()
    if (
      typeof payload === 'object' &&
      payload !== null &&
      'detail' in payload &&
      typeof (payload as { detail: unknown }).detail === 'string'
    ) {
      message = (payload as { detail: string }).detail
    }
  } catch {
    // Keep the default message when the body is not JSON.
  }
  return new ApiError(response.status, message)
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, init)
  if (!response.ok) {
    throw await parseError(response)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export const api = {
  listReviews(): Promise<ReviewSummary[]> {
    return request('/api/documents')
  },

  getReview(id: string): Promise<ReviewDetail> {
    return request(`/api/documents/${id}`)
  },

  async createReview(file: File): Promise<ReviewDetail> {
    const body = new FormData()
    body.append('file', file)
    return request('/api/documents', { method: 'POST', body })
  },

  updateReview(id: string, fields: ReviewFields): Promise<ReviewDetail> {
    return request(`/api/documents/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields }),
    })
  },

  updateAccounting(id: string, glAccountCode: string): Promise<ReviewDetail> {
    return request(`/api/documents/${id}/accounting`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gl_account_code: glAccountCode }),
    })
  },

  decide(id: string, decision: 'approve' | 'reject'): Promise<ReviewDetail> {
    return request(`/api/documents/${id}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision }),
    })
  },

  draftCorrectionEmail(id: string): Promise<CorrectionEmail> {
    return request(`/api/documents/${id}/correction-email`, { method: 'POST' })
  },

  deleteReview(id: string): Promise<void> {
    return request(`/api/documents/${id}`, { method: 'DELETE' })
  },

  listGlAccounts(): Promise<GLAccount[]> {
    return request('/api/accounting/gl-accounts')
  },

  documentFileUrl(id: string): string {
    return `${env.apiBaseUrl}/api/documents/${id}/file`
  },
}

export { ApiError }
