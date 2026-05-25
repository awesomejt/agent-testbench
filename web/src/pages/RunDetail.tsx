import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchRun, type Run } from '@/lib/api'
import { Badge } from '@/components/ui/badge'

function Metric({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-medium">{children}</span>
    </div>
  )
}

function fmt(dt: string | null) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export default function RunDetail() {
  const { id } = useParams<{ id: string }>()
  const [run, setRun] = useState<Run | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    fetchRun(Number(id))
      .then(setRun)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="p-6 text-muted-foreground text-sm">Loading…</p>
  if (error)   return <p className="p-6 text-destructive text-sm">{error}</p>
  if (!run)    return null

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Link to="/runs" className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block">
        ← Back to runs
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-semibold font-mono">{run.scenario_name}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{run.run_name}</p>
        </div>
        {run.pass_fail && (
          <Badge variant={run.pass_fail} className="text-sm px-3 py-1">
            {run.pass_fail}
          </Badge>
        )}
      </div>

      {/* Metrics grid */}
      <div className="rounded-md border border-border bg-card p-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        <Metric label="Model">{run.model_name}</Metric>
        <Metric label="Provider">{run.provider}</Metric>
        {run.agent_server && <Metric label="Agent server">{run.agent_server}</Metric>}
        <Metric label="Score">
          {run.score != null ? run.score.toFixed(2) : '—'}
        </Metric>
        <Metric label="Duration">{run.total_time.toFixed(2)}s</Metric>
        {run.tokens_per_second != null && (
          <Metric label="Tok/s">{run.tokens_per_second.toFixed(1)}</Metric>
        )}
        <Metric label="Tokens">
          {run.input_tokens} in / {run.output_tokens} out / {run.total_tokens} total
        </Metric>
        {run.cost_usd != null && (
          <Metric label="Cost">${run.cost_usd.toFixed(4)}</Metric>
        )}
        <Metric label="Started">{fmt(run.start_datetime)}</Metric>
        {run.error && (
          <Metric label="Error">
            <span className="text-destructive">{run.error_message ?? 'yes'}</span>
          </Metric>
        )}
      </div>

      {/* Model output */}
      {run.output_text && (
        <section className="mb-6">
          <h2 className="text-sm font-medium mb-2">Model output</h2>
          <pre className="rounded-md border border-border bg-muted p-4 text-sm font-mono whitespace-pre-wrap break-words">
            {run.output_text}
          </pre>
        </section>
      )}

      {/* Grader section */}
      {run.grader_model && (
        <section>
          <h2 className="text-sm font-medium mb-2">
            Grader — <span className="font-normal text-muted-foreground">{run.grader_model}</span>
          </h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {run.grader_rationale ?? '—'}
          </p>
        </section>
      )}
    </div>
  )
}
