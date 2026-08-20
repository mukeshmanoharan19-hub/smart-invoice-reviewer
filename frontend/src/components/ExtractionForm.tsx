import { emptyToNull, formatConfidence } from '../lib/format'
import type { FieldSource, ReviewFields } from '../lib/types'

type Props = {
  fields: ReviewFields
  disabled?: boolean
  onChange: (fields: ReviewFields) => void
}

function Field({
  label,
  value,
  confidence,
  source,
  disabled,
  onChange,
}: {
  label: string
  value: string
  confidence?: number | null
  source?: FieldSource | null
  disabled?: boolean
  onChange: (value: string) => void
}) {
  return (
    <label className="block text-sm">
      <span className="font-medium text-slate-800">{label}</span>
      {source ? (
        <span className="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-600">
          {source}
        </span>
      ) : null}
      {confidence !== undefined && confidence !== null && source !== 'human' ? (
        <span className="ml-2 text-xs text-slate-500">
          confidence {formatConfidence(confidence)}
        </span>
      ) : null}
      <input
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  )
}

export function ExtractionForm({ fields, disabled = false, onChange }: Props) {
  const update = (patch: Partial<ReviewFields>) => onChange({ ...fields, ...patch })
  const sourceOf = (name: string) => fields.field_sources?.[name] ?? null

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Field
        label={fields.document_type === 'receipt' ? 'Merchant name' : 'Vendor name'}
        value={fields.vendor_name ?? ''}
        confidence={fields.vendor_name_confidence}
        source={sourceOf('vendor_name')}
        disabled={disabled}
        onChange={(value) => update({ vendor_name: emptyToNull(value) })}
      />
      <Field
        label={fields.document_type === 'receipt' ? 'Merchant GSTIN' : 'Vendor GSTIN'}
        value={fields.vendor_gstin ?? ''}
        confidence={fields.vendor_gstin_confidence}
        source={sourceOf('vendor_gstin')}
        disabled={disabled}
        onChange={(value) => update({ vendor_gstin: emptyToNull(value) })}
      />
      <Field
        label="Vendor address"
        value={fields.vendor_address ?? ''}
        source={sourceOf('vendor_address')}
        disabled={disabled}
        onChange={(value) => update({ vendor_address: emptyToNull(value) })}
      />
      <Field
        label="Customer name"
        value={fields.customer_name ?? ''}
        confidence={fields.customer_name_confidence}
        source={sourceOf('customer_name')}
        disabled={disabled || fields.document_type === 'receipt'}
        onChange={(value) => update({ customer_name: emptyToNull(value) })}
      />
      <Field
        label="Customer GSTIN"
        value={fields.customer_gstin ?? ''}
        confidence={fields.customer_gstin_confidence}
        source={sourceOf('customer_gstin')}
        disabled={disabled || fields.document_type === 'receipt'}
        onChange={(value) => update({ customer_gstin: emptyToNull(value) })}
      />
      <Field
        label="Invoice number"
        value={fields.invoice_number ?? ''}
        confidence={fields.invoice_number_confidence}
        source={sourceOf('invoice_number')}
        disabled={disabled || fields.document_type === 'receipt'}
        onChange={(value) => update({ invoice_number: emptyToNull(value) })}
      />
      <Field
        label={fields.document_type === 'receipt' ? 'Transaction date' : 'Invoice date'}
        value={fields.invoice_date ?? ''}
        confidence={fields.invoice_date_confidence}
        source={sourceOf('invoice_date')}
        disabled={disabled}
        onChange={(value) => update({ invoice_date: emptyToNull(value) })}
      />
      <Field
        label="Due date"
        value={fields.due_date ?? ''}
        confidence={fields.due_date_confidence}
        source={sourceOf('due_date')}
        disabled={disabled || fields.document_type === 'receipt'}
        onChange={(value) => update({ due_date: emptyToNull(value) })}
      />
      <Field
        label="Purchase order"
        value={fields.purchase_order ?? ''}
        confidence={fields.purchase_order_confidence}
        source={sourceOf('purchase_order')}
        disabled={disabled || fields.document_type === 'receipt'}
        onChange={(value) => update({ purchase_order: emptyToNull(value) })}
      />
      <Field
        label="Currency"
        value={fields.currency ?? ''}
        source={sourceOf('currency')}
        disabled={disabled}
        onChange={(value) => update({ currency: emptyToNull(value) })}
      />
      <Field
        label="Subtotal"
        value={fields.subtotal ?? ''}
        confidence={fields.subtotal_confidence}
        source={sourceOf('subtotal')}
        disabled={disabled}
        onChange={(value) => update({ subtotal: emptyToNull(value) })}
      />
      <Field
        label="Total tax"
        value={fields.total_tax ?? ''}
        confidence={fields.total_tax_confidence}
        source={sourceOf('total_tax')}
        disabled={disabled}
        onChange={(value) => update({ total_tax: emptyToNull(value) })}
      />
      <Field
        label="Total"
        value={fields.total ?? ''}
        confidence={fields.total_confidence}
        source={sourceOf('total')}
        disabled={disabled}
        onChange={(value) => update({ total: emptyToNull(value) })}
      />
      <div className="text-sm text-slate-600 md:col-span-2">
        Document type: <span className="font-medium">{fields.document_type}</span>
        {fields.document_confidence !== null ? (
          <span className="ml-3">
            Self-reported confidence {formatConfidence(fields.document_confidence)}
          </span>
        ) : null}
        <p className="mt-1 text-xs text-slate-500">
          Saving corrections marks changed fields as human and re-runs Northstar policy.
        </p>
      </div>
    </div>
  )
}
