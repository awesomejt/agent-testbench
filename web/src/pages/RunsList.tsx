import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchRuns, type Run, type RunsFilter } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/ui/table'

function passFail(run: Run) {
  const v = run.pass_fail
  if (!v) return <span className="text-muted-foreground">—</span>
  return <Badge variant={v}>{v}</Badge>
}

function fmt(dt: string | null) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

function fmtDuration(s: number) {
  return s < 60 ? `${s.toFixed(1)}s` : `${(s / 60).toFixed(1)}m`
}

export default function RunsList() {
  const navigate = useNavigate()
  const [runs, setRuns] = useState<Run[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<RunsFilter>({})
  const [draft, setDraft] = useState<RunsFilter>({})

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetchRuns(filter)
      .then(setRuns)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [filter])

  function applyFilter(e: React.FormEvent) {
    e.preventDefault()
    setFilter({ ...draft })
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Runs</h1>

      {/* Filter bar */}
      <form onSubmit={applyFilter} className="flex flex-wrap gap-2 mb-6">
        <input
          className="rounded-md border border-border bg-card px-3 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="Scenario"
          value={draft.scenario ?? ''}
          onChange={e => setDraft(d => ({ ...d, scenario: e.target.value || undefined }))}
        />
        <input
          className="rounded-md border border-border bg-card px-3 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="Model"
          value={draft.model ?? ''}
          onChange={e => setDraft(d => ({ ...d, model: e.target.value || undefined }))}
        />
        <input
          className="rounded-md border border-border bg-card px-3 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="Provider"
          value={draft.provider ?? ''}
          onChange={e => setDraft(d => ({ ...d, provider: e.target.value || undefined }))}
        />
        <button
          type="submit"
          className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Filter
        </button>
        {Object.keys(filter).length > 0 && (
          <button
            type="button"
            className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent"
            onClick={() => { setFilter({}); setDraft({}) }}
          >
            Clear
          </button>
        )}
      </form>

      {error && (
        <p className="text-destructive text-sm mb-4">{error}</p>
      )}

      {loading ? (
        <p className="text-muted-foreground text-sm">Loading…</p>
      ) : runs.length === 0 ? (
        <p className="text-muted-foreground text-sm">No runs found.</p>
      ) : (
        <div className="rounded-md border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Scenario</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Provider</TableHead>
                <TableHead>Result</TableHead>
                <TableHead className="text-right">Score</TableHead>
                <TableHead className="text-right">Duration</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map(run => (
                <TableRow key={run.id} onClick={() => navigate(`/runs/${run.id}`)}>
                  <TableCell className="font-mono text-xs">{run.scenario_name}</TableCell>
                  <TableCell>{run.model_name}</TableCell>
                  <TableCell className="text-muted-foreground">{run.provider}</TableCell>
                  <TableCell>{passFail(run)}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {run.score != null ? run.score.toFixed(2) : '—'}
                  </TableCell>
                  <TableCell className="text-right tabular-nums text-muted-foreground">
                    {fmtDuration(run.total_time)}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {fmt(run.start_datetime)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
