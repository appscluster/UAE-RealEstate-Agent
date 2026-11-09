import { useEffect, useRef, useState } from 'react'

const KEY = 'readiness-session'
const MODEL_KEY = 'readiness-model'

type DealSummary = {
  deal_id: string
  project: string
  unit_id: string
  asking_price_aed: number
}

type Deal = DealSummary & {
  developer: string
  jurisdiction: string
  buyer_question: string
  documents: Array<{ id: string; title: string; banner: string; issuer_label?: string; sections?: Record<string, string> }>
}

type Step = {
  seq: number
  phase?: string
  agent?: string
  verdict?: string
  conflicts?: string[]
  refused?: string
  event?: string
  line?: string
}

type Draft = {
  text: string
  price_is_fair: boolean
  sent_to_buyer: boolean
  warnings: Array<{ code: string; detail: string }>
  citations: string[]
  model: string
  requested_model?: string
  fallback_reason?: string
  usage?: { prompt_tokens?: number; completion_tokens?: number }
}

const DECISION_NOTE = {
  approve: 'The report is accepted for this file. Nothing is sent to a buyer.',
  reject: 'The report is back with the coordinator. Nothing is sent to a buyer.',
  escalate: 'The case is with the pod lead. Nothing is sent to a buyer.',
}

type Finding = {
  agent: string
  note?: string
  manual_links?: Array<{ label: string; url: string; note: string }>
  lines?: Array<{ name: string; aed: number; basis: string }>
}

function base(): string {
  if (import.meta.env.DEV) return ''
  return (window as unknown as { __API_BASE__?: string }).__API_BASE__ || ''
}

function money(value: number): string {
  return `${value.toLocaleString('en-AE')} AED`
}

export function App() {
  const [authed, setAuthed] = useState(localStorage.getItem(KEY) === 'coordinator')
  if (!authed) return <Gate onOk={() => setAuthed(true)} />
  return <Desk onSignOut={() => { localStorage.removeItem(KEY); setAuthed(false) }} />
}

function Gate({ onOk }: { onOk: () => void }) {
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  return (
    <main className="gate">
      <form onSubmit={(event) => {
        event.preventDefault()
        if (name.trim().toLowerCase() === 'coordinator' && password === 'demo') onOk()
        else setError('That sign in was not recognised.')
        if (name.trim().toLowerCase() === 'coordinator' && password === 'demo') {
          localStorage.setItem(KEY, 'coordinator')
        }
      }}>
        <p className="eyebrow">Sandstone Realty</p>
        <h1>Readiness</h1>
        <p className="lede">A deal file for one fictional Dubai brokerage. The papers are synthetic.</p>
        <label htmlFor="name">Name</label>
        <input id="name" value={name} onChange={(event) => setName(event.target.value)} autoComplete="username" />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
        <div className="row">
          <button className="solid" type="submit">Open the file</button>
        </div>
        {error ? <p className="hint">{error}</p> : <p className="lede">Use coordinator / demo.</p>}
      </form>
    </main>
  )
}

function Spinner() {
  return <span className="spin" aria-hidden="true" />
}

function busyLabel(busy: string): string {
  if (busy === 'abu') return 'Checking the Abu Dhabi question.'
  if (busy === 'read') return 'Reading the deal.'
  if (busy === 'approve') return 'Accepting the report.'
  if (busy === 'reject') return 'Sending the report back.'
  if (busy === 'escalate') return 'Escalating the case.'
  return ''
}

function excerpt(doc: Deal['documents'][number]): string {
  const first = Object.values(doc.sections || {})[0]
  return typeof first === 'string' ? first : ''
}

function refusalText(reason: string): string {
  if (reason === 'jurisdiction') {
    return 'This Dubai checklist does not validate an Abu Dhabi Aldar sale. The jurisdiction reviewer reads the open Dubai file. No Abu Dhabi pack is loaded.'
  }
  if (reason === 'cross_tenant') {
    return 'No findings were read from another brokerage.'
  }
  if (reason === 'load_failed') {
    return 'The deal file could not be loaded.'
  }
  if (reason === 'run_failed') {
    return 'The run did not start.'
  }
  return `The planner stopped. Reason: ${reason}.`
}

function fallbackText(draft: Draft): string {
  const requested = draft.requested_model || 'the selected model'
  if ((draft.fallback_reason || '').includes('not accessible') || (draft.fallback_reason || '').includes('unsupported_api')) {
    return `${requested} cannot be called on chat completions. This report is the template.`
  }
  return `OmniRoute did not answer for ${requested}. This report is the template.`
}

function Desk({ onSignOut }: { onSignOut: () => void }) {
  const [files, setFiles] = useState<DealSummary[]>([])
  const [deal, setDeal] = useState<Deal | null>(null)
  const [steps, setSteps] = useState<Step[]>([])
  const [opened, setOpened] = useState<string[]>(['Agent log is ready. Open a file, then read the deal.'])
  const [extra, setExtra] = useState<string[]>([])
  const [draft, setDraft] = useState<Draft | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [refusal, setRefusal] = useState('')
  const [note, setNote] = useState('')
  const [decision, setDecision] = useState('')
  const [busy, setBusy] = useState('')
  const [runId, setRunId] = useState('')
  const [models, setModels] = useState<string[]>(['template'])
  const [model, setModel] = useState(() => localStorage.getItem(MODEL_KEY) || 'template')

  function chooseModel(next: string) {
    setModel(next)
    localStorage.setItem(MODEL_KEY, next)
  }
  const logRef = useRef<HTMLOListElement>(null)
  const generation = useRef(0)
  const sourceRef = useRef<EventSource | null>(null)

  function beginAction() {
    generation.current += 1
    sourceRef.current?.close()
    sourceRef.current = null
    return generation.current
  }

  function loadDeal(dealId: string) {
    const token = beginAction()
    setDraft(null)
    setFindings([])
    setSteps([])
    setExtra([])
    setNote('')
    setDecision('')
    setBusy('')
    setRefusal('')
    setRunId('')
    fetch(base() + `/api/deals/${dealId}`)
      .then((response) => {
        if (!response.ok) throw new Error('load')
        return response.json()
      })
      .then((body) => {
        if (token !== generation.current) return
        const next = body.deal as Deal
        setDeal(next)
        setOpened([
          `Opened ${next.project}, unit ${next.unit_id}. Asking ${money(next.asking_price_aed)}.`,
          `${next.documents.length} synthetic documents are on the file. No live DLD check has been made.`,
        ])
      })
      .catch(() => {
        if (token !== generation.current) return
        setRefusal('load_failed')
      })
  }

  useEffect(() => {
    fetch(base() + '/api/models')
      .then((response) => response.json())
      .then((body) => {
        const list = (body.models || ['template']) as string[]
        setModels(list)
        const saved = localStorage.getItem(MODEL_KEY)
        if (saved && list.includes(saved)) setModel(saved)
        else if (body.default) chooseModel(body.default)
      })
      .catch(() => setModels(['template']))
    fetch(base() + '/api/deals')
      .then((response) => response.json())
      .then((body) => {
        const list = (body.deals || []) as DealSummary[]
        setFiles(list)
        if (list[0]) loadDeal(list[0].deal_id)
      })
      .catch(() => setRefusal('The deal file could not be loaded.'))
  }, [])

  useEffect(() => {
    const node = logRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [opened, steps, extra])

  function readDeal(extraBody: Record<string, string> = {}) {
    if (!deal) return
    const token = beginAction()
    const dealId = deal.deal_id
    setSteps([])
    setExtra([])
    setDraft(null)
    setFindings([])
    setRefusal('')
    setNote('')
    setDecision('')
    setBusy(extraBody.question ? 'abu' : 'read')
    fetch(base() + '/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deal_id: dealId, model, ...extraBody }),
    })
      .then((response) => {
        if (!response.ok) throw new Error('run')
        return response.json()
      })
      .then((body) => {
        if (token !== generation.current) return
        setRunId(body.run_id)
        if (body.refused) setRefusal(body.refusal_reason || 'refused')
        const source = new EventSource(base() + `/runs/${body.run_id}/events`)
        sourceRef.current = source
        source.onmessage = (message) => {
          if (token !== generation.current) {
            source.close()
            return
          }
          const event = JSON.parse(message.data) as Step
          if (event.event === 'done') {
            source.close()
            fetch(base() + `/api/runs/${body.run_id}`)
              .then((response) => response.json())
              .then((loaded) => {
                if (token !== generation.current) return
                setDraft(loaded.run.draft || null)
                setFindings(loaded.run.findings || [])
                if (loaded.run.refused) setRefusal(loaded.run.refusal_reason || 'refused')
                setBusy('')
              })
            return
          }
          if (!event.phase) return
          setSteps((current) => current.some((item) => item.seq === event.seq) ? current : [...current, event])
        }
      })
      .catch(() => {
        if (token !== generation.current) return
        setBusy('')
        setRefusal('run_failed')
      })
  }

  function decide(choice: 'approve' | 'reject' | 'escalate') {
    if (!runId || busy) return
    const token = generation.current
    setBusy(choice)
    fetch(base() + `/api/runs/${runId}/decisions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision: choice, actor: 'manager:demo' }),
    })
      .then(async (response) => {
        const body = await response.json().catch(() => ({}))
        if (token !== generation.current) return
        setBusy('')
        if (!response.ok) return
        const label = choice === 'approve' ? 'Approved' : choice === 'reject' ? 'Sent back' : 'Escalated'
        const line = `${label}. ${body.delivery?.note || DECISION_NOTE[choice]}`
        setDecision(choice)
        setNote(line)
        setExtra([line])
      })
      .catch(() => {
        if (token !== generation.current) return
        setBusy('')
      })
  }

  const permit = findings.find((item) => item.agent === 'permit')
  const cost = findings.find((item) => item.agent === 'cost')
  const jurisdiction = findings.find((item) => item.agent === 'jurisdiction')

  const logLines = [...opened, ...steps.map((step) => step.line).filter((line): line is string => Boolean(line)), ...extra]

  return (
    <main className="desk">
      <header className="mast">
        <div>
          <p className="eyebrow">Sandstone Realty · Dubai</p>
          <h1>{deal?.project || 'Canal Courtyard'}</h1>
        </div>
        <div>
          <span className="seal">SYNTHETIC DEMO</span>
          <div className="row">
            <a className="texty" href="/explain">The assignment</a>
            <button className="texty" type="button" onClick={onSignOut}>Sign out</button>
          </div>
        </div>
      </header>
      <div className="work">
        <aside className="files" aria-label="Deal files">
          {files.map((file) => (
            <button
              key={file.deal_id}
              className={file.deal_id === deal?.deal_id ? 'file on' : 'file'}
              type="button"
              onClick={() => loadDeal(file.deal_id)}
            >
              <b>{file.project}</b>
              <span>{file.unit_id} · {money(file.asking_price_aed)}</span>
            </button>
          ))}
        </aside>
        <div className="work-main">
      {deal && (
        <>
          <p className="facts">
            <span>Unit <strong>{deal.unit_id}</strong></span>
            <span>Developer <strong>{deal.developer}</strong></span>
            <span>Jurisdiction <strong>{deal.jurisdiction}</strong></span>
            <span>Asking <strong>{money(deal.asking_price_aed)}</strong></span>
          </p>
          <p>{deal.buyer_question}</p>
          <div className="slips">
            {deal.documents.map((doc) => (
              <article key={doc.id} className="slip">
                <b>{doc.title}</b>
                <span>{doc.banner}{doc.issuer_label ? ` · ${doc.issuer_label}` : ''}</span>
                <span>{excerpt(doc)}</span>
              </article>
            ))}
          </div>
        </>
      )}
      <div className="actions">
        <label htmlFor="model">Model</label>
        <select id="model" value={model} onChange={(event) => chooseModel(event.target.value)}>
          {models.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <button className="solid" type="button" disabled={Boolean(busy)} aria-busy={busy === 'read'} onClick={() => readDeal()}>{busy === 'read' ? <Spinner /> : null}Read the deal</button>
        <button className="quiet" type="button" disabled={Boolean(busy)} aria-busy={busy === 'abu'} onClick={() => readDeal({ question: 'Can this Dubai checklist validate an Abu Dhabi Aldar sale?' })}>{busy === 'abu' ? <Spinner /> : null}Check an Abu Dhabi sale</button>
      </div>
      <section className="sheet">
        <article className="letter">
          <h2>Deal writer</h2>
          {refusal && refusal !== 'in_scope' ? (
            <p className="warning">{refusalText(refusal)}</p>
          ) : null}
          {draft ? (
            <>
              {draft.fallback_reason ? <p className="warning">{fallbackText(draft)}</p> : null}
              {jurisdiction?.note ? <p className="warning">{jurisdiction.note}</p> : null}
              <p>{draft.text}</p>
              {draft.warnings.map((warning) => (
                <p key={warning.code} className="warning">{warning.detail}</p>
              ))}
              {cost?.lines ? (
                <ul>
                  {cost.lines.map((line) => (
                    <li key={line.name}>{line.name}: {money(line.aed)}. {line.basis}</li>
                  ))}
                </ul>
              ) : null}
              <p className="cites">Citations: {draft.citations.join(', ')}. Model: {draft.model}.{draft.usage?.prompt_tokens ? ` ${draft.usage.prompt_tokens} prompt tokens, ${draft.usage.completion_tokens || 0} completion tokens.` : ''}</p>
              {permit?.manual_links ? (
                <ul className="links">
                  {permit.manual_links.map((link) => (
                    <li key={link.url}><a href={link.url}>{link.label}</a>. {link.note}</li>
                  ))}
                </ul>
              ) : null}
              <p>Nothing is sent to a buyer.</p>
              <div className="actions">
                <button className={decision === 'approve' || !decision ? 'solid' : 'quiet'} type="button" disabled={Boolean(busy)} aria-busy={busy === 'approve'} aria-pressed={decision === 'approve'} onClick={() => decide('approve')}>{busy === 'approve' ? <Spinner /> : null}Approve the report</button>
                <button className={decision === 'reject' ? 'solid' : 'quiet'} type="button" disabled={Boolean(busy)} aria-busy={busy === 'reject'} aria-pressed={decision === 'reject'} onClick={() => decide('reject')}>{busy === 'reject' ? <Spinner /> : null}Send it back</button>
                <button className={decision === 'escalate' ? 'solid' : 'quiet'} type="button" disabled={Boolean(busy)} aria-busy={busy === 'escalate'} aria-pressed={decision === 'escalate'} onClick={() => decide('escalate')}>{busy === 'escalate' ? <Spinner /> : null}Escalate</button>
              </div>
              {note ? <p>{note}</p> : null}
            </>
          ) : refusal ? null : busy === 'read' || busy === 'abu' ? (
            <p className="lede" role="status"><Spinner />{busyLabel(busy)}</p>
          ) : <p className="lede">The report appears here after the critic has read the specialists.</p>}
        </article>
      </section>
        </div>
      </div>
      <section className="agent-log" aria-label="Agent log">
        <div className="agent-log-head">
          <h2>Agent log</h2>
          <span>{logLines.length} lines</span>
        </div>
        <ol ref={logRef}>
          {logLines.map((line, index) => <li key={`${index}-${line}`}>{line}</li>)}
        </ol>
      </section>
    </main>
  )
}
