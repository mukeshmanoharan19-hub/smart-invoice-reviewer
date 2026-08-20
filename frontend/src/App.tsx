import { useEffect, useMemo, useState } from 'react'
import { ApiError, api } from './lib/api'
import type {
  CorrectionEmail,
  GLAccount,
  ReviewDetail,
  ReviewFields,
  ReviewSummary,
} from './lib/types'
import { ClassificationPanel } from './components/ClassificationPanel'
import { CorrectionEmailDialog } from './components/CorrectionEmailDialog'
import { DecisionBar } from './components/DecisionBar'
import { DocumentInbox } from './components/DocumentInbox'
import { ExtractionForm } from './components/ExtractionForm'
import { GLAccountSelect } from './components/GLAccountSelect'
import { IssueList } from './components/IssueList'
import { ProcessingStep } from './components/ProcessingStep'
import { UploadStep } from './components/UploadStep'
import { WelcomePortal } from './components/WelcomePortal'
import { Button } from './components/ui/Button'
import { Panel } from './components/ui/Panel'

type Screen = 'welcome' | 'upload' | 'processing' | 'review'

export default function App() {
  const [screen, setScreen] = useState<Screen>('welcome')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [reviews, setReviews] = useState<ReviewSummary[]>([])
  const [accounts, setAccounts] = useState<GLAccount[]>([])
  const [activeReview, setActiveReview] = useState<ReviewDetail | null>(null)
  const [draftFields, setDraftFields] = useState<ReviewFields | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [emailDraft, setEmailDraft] = useState<CorrectionEmail | null>(null)

  const canApprove = useMemo(() => {
    if (!activeReview) {
      return false
    }
    return (
      activeReview.status === 'pending' &&
      Boolean(activeReview.gl_account_code) &&
      !activeReview.issues.some((issue) => issue.severity === 'error')
    )
  }, [activeReview])

  useEffect(() => {
    void refreshLists()
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  async function refreshLists() {
    try {
      const [nextReviews, nextAccounts] = await Promise.all([
        api.listReviews(),
        api.listGlAccounts(),
      ])
      setReviews(nextReviews)
      setAccounts(nextAccounts)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    }
  }

  function chooseFile(file: File) {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setError(null)
    setScreen('upload')
  }

  function chooseAnotherFile() {
    setSelectedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setPreviewUrl(null)
    setScreen('welcome')
  }

  async function processSelectedFile() {
    if (!selectedFile) {
      return
    }
    setBusy(true)
    setError(null)
    setScreen('processing')
    try {
      const review = await api.createReview(selectedFile)
      setActiveReview(review)
      setDraftFields(review.fields)
      setScreen('review')
      await refreshLists()
    } catch (err) {
      setScreen('upload')
      setError(err instanceof ApiError || err instanceof Error ? err.message : 'Processing failed')
    } finally {
      setBusy(false)
    }
  }

  async function openReview(id: string) {
    setBusy(true)
    setError(null)
    try {
      const review = await api.getReview(id)
      setActiveReview(review)
      setDraftFields(review.fields)
      setScreen('review')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open document')
    } finally {
      setBusy(false)
    }
  }

  async function saveCorrections() {
    if (!activeReview || !draftFields) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      const review = await api.updateReview(activeReview.id, draftFields)
      setActiveReview(review)
      setDraftFields(review.fields)
      await refreshLists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save corrections')
    } finally {
      setBusy(false)
    }
  }

  async function changeGlAccount(code: string) {
    if (!activeReview || !code) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      const review = await api.updateAccounting(activeReview.id, code)
      setActiveReview(review)
      setDraftFields(review.fields)
      await refreshLists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update GL account')
    } finally {
      setBusy(false)
    }
  }

  async function decide(decision: 'approve' | 'reject') {
    if (!activeReview) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      const review = await api.decide(activeReview.id, decision)
      setActiveReview(review)
      setDraftFields(review.fields)
      await refreshLists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Decision failed')
    } finally {
      setBusy(false)
    }
  }

  async function draftEmail() {
    if (!activeReview) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      const draft = await api.draftCorrectionEmail(activeReview.id)
      setEmailDraft(draft)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to draft correction email')
    } finally {
      setBusy(false)
    }
  }

  async function deleteReview(id: string) {
    setBusy(true)
    setError(null)
    try {
      await api.deleteReview(id)
      if (activeReview?.id === id) {
        setActiveReview(null)
        setDraftFields(null)
        setScreen('welcome')
      }
      await refreshLists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-8 lg:px-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Northstar Facilities
          </p>
          <h1 className="mt-1 text-3xl font-semibold text-slate-900">Invoice Review</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            The frontend holds no business logic. Every button becomes an API call; Python owns
            classification, extraction, policy, and GL suggestion.
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => {
            setScreen('welcome')
            setActiveReview(null)
            setDraftFields(null)
            setError(null)
          }}
        >
          Start over
        </Button>
      </header>

      {error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <DocumentInbox
          reviews={reviews}
          selectedId={activeReview?.id ?? null}
          onSelect={(id) => void openReview(id)}
          onDelete={(id) => void deleteReview(id)}
        />

        <div className="space-y-6">
          {screen === 'welcome' ? (
            <WelcomePortal busy={busy} onFileSelected={chooseFile} />
          ) : null}

          {screen === 'upload' ? (
            <UploadStep
              file={selectedFile}
              previewUrl={previewUrl}
              busy={busy}
              onProcess={() => void processSelectedFile()}
              onChooseAnother={chooseAnotherFile}
            />
          ) : null}

          {screen === 'processing' ? (
            <ProcessingStep file={selectedFile} previewUrl={previewUrl} />
          ) : null}

          {screen === 'review' && activeReview && draftFields ? (
            <>
              <ClassificationPanel review={activeReview} />

              <Panel>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Extraction</h2>
                    <p className="mt-1 text-sm text-slate-600">
                      {activeReview.filename} · status {activeReview.status}
                    </p>
                  </div>
                </div>
                <div className="mt-5">
                  <ExtractionForm
                    fields={draftFields}
                    disabled={busy || activeReview.status !== 'pending'}
                    onChange={setDraftFields}
                  />
                </div>
                {activeReview.status === 'pending' ? (
                  <div className="mt-4">
                    <Button onClick={() => void saveCorrections()} disabled={busy}>
                      Save corrections and re-check policy
                    </Button>
                  </div>
                ) : null}
              </Panel>

              <div className="grid gap-6 md:grid-cols-2">
                <Panel>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Validation
                  </h3>
                  <div className="mt-4">
                    <IssueList issues={activeReview.issues} />
                  </div>
                </Panel>
                <Panel>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    GL suggestion
                  </h3>
                  <div className="mt-4">
                    <GLAccountSelect
                      accounts={accounts}
                      value={activeReview.gl_account_code}
                      suggestionCode={activeReview.gl_suggestion?.account_code ?? null}
                      suggestionRationale={activeReview.gl_suggestion?.reasoning ?? null}
                      disabled={busy || activeReview.status !== 'pending'}
                      onChange={(code) => void changeGlAccount(code)}
                    />
                  </div>
                </Panel>
              </div>

              {activeReview.status === 'pending' ? (
                <Panel>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Decision
                  </h3>
                  <div className="mt-4">
                    <DecisionBar
                      disabled={busy}
                      canApprove={canApprove}
                      canDraftEmail={activeReview.correction_email_eligible}
                      onApprove={() => void decide('approve')}
                      onReject={() => void decide('reject')}
                      onDraftEmail={() => void draftEmail()}
                    />
                  </div>
                </Panel>
              ) : (
                <Panel>
                  <p className="text-sm text-slate-700">
                    This review is <span className="font-medium">{activeReview.status}</span>. You can
                    still draft a correction email or delete it from the inbox to reset the demo.
                  </p>
                  <div className="mt-4">
                    <Button
                      variant="secondary"
                      onClick={() => void draftEmail()}
                      disabled={busy || !activeReview.correction_email_eligible}
                    >
                      Draft correction email
                    </Button>
                  </div>
                </Panel>
              )}
            </>
          ) : null}
        </div>
      </div>

      <CorrectionEmailDialog draft={emailDraft} onClose={() => setEmailDraft(null)} />
    </div>
  )
}
