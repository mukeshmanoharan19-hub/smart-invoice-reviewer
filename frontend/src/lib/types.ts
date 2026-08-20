export type DocumentType = 'invoice' | 'receipt'
export type ReviewStatus = 'pending' | 'approved' | 'rejected'
export type IssueSeverity = 'error' | 'warning'
export type FieldSource = 'openai' | 'human'

export type ReviewLineItem = {
  description: string | null
  quantity: string | null
  unit_price: string | null
  amount: string | null
  tax: string | null
}

export type ReviewFields = {
  document_type: DocumentType
  vendor_name: string | null
  vendor_name_confidence: number | null
  vendor_gstin: string | null
  vendor_gstin_confidence: number | null
  vendor_address: string | null
  customer_name: string | null
  customer_name_confidence: number | null
  customer_gstin: string | null
  customer_gstin_confidence: number | null
  customer_address: string | null
  invoice_number: string | null
  invoice_number_confidence: number | null
  invoice_date: string | null
  invoice_date_confidence: number | null
  due_date: string | null
  due_date_confidence: number | null
  purchase_order: string | null
  purchase_order_confidence: number | null
  currency: string | null
  subtotal: string | null
  subtotal_confidence: number | null
  total_tax: string | null
  total_tax_confidence: number | null
  total: string | null
  total_confidence: number | null
  document_confidence: number | null
  field_sources: Record<string, FieldSource>
  line_items: ReviewLineItem[]
}

export type Issue = {
  code: string
  severity: IssueSeverity
  message: string
  field: string | null
}

export type ReviewSummary = {
  id: string
  filename: string
  document_type: DocumentType
  status: ReviewStatus
  vendor_name: string | null
  invoice_number: string | null
  total: string | null
  currency: string | null
  created_at: string
  updated_at: string
}

export type ReviewDetail = {
  id: string
  filename: string
  content_type: string
  document_type: DocumentType
  status: ReviewStatus
  fields: ReviewFields
  issues: Issue[]
  classification: {
    document_kind: DocumentType
    confidence: number
    reasoning: string
  } | null
  gl_suggestion: {
    account_code: string
    confidence: number
    reasoning: string
  } | null
  gl_account_code: string | null
  correction_email_eligible: boolean
  created_at: string
  updated_at: string
  decided_at: string | null
}

export type GLAccount = {
  code: string
  name: string
  description: string
}

export type CorrectionEmail = {
  subject: string
  body: string
}
