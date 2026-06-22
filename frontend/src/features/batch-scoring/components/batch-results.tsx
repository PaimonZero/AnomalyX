import { AlertTriangle, Check, Download, LoaderCircle, RotateCcw } from "lucide-react";

import { RiskBadge } from "@/features/alerts/components/alert-badges";
import type { BatchResultRow } from "@/features/batch-scoring/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";

interface BatchResultsProps {
  rows: BatchResultRow[];
  error: string | null;
  running: boolean;
  processed: number;
  total: number;
  flagged: number;
  failed: number;
  riskFilter: "ALL" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  flaggedOnly: boolean;
  onRiskFilterChange: (value: BatchResultsProps["riskFilter"]) => void;
  onFlaggedOnlyChange: (value: boolean) => void;
  onOpen: (row: BatchResultRow) => void;
  onExport: () => void;
  onRetryFailed: () => void;
}

const formatAmount = (value: number, currency: string) => `${new Intl.NumberFormat("en-US").format(value)} ${currency}`;

export function BatchResults(props: BatchResultsProps) {
  const scoredRows = props.rows.filter((row) => row.prediction);
  const averageRisk = scoredRows.length
    ? scoredRows.reduce((sum, row) => sum + (row.prediction?.risk_score ?? 0), 0) / scoredRows.length
    : 0;
  const filteredRows = props.rows
    .filter((row) => props.riskFilter === "ALL" || row.prediction?.risk_level === props.riskFilter)
    .filter((row) => !props.flaggedOnly || row.prediction?.is_flagged)
    .sort((left, right) => (right.prediction?.risk_score ?? -1) - (left.prediction?.risk_score ?? -1));

  if (props.running) {
    return (
      <section className="batch-results-panel batch-progress-state">
        <div className="batch-results-heading"><div><LoaderCircle className="spin" size={17} /><span>Waiting for backend processing…</span></div><code>{props.total} rows</code></div>
        <div className="batch-progress-track batch-progress-track--indeterminate"><span /></div>
        <div className="batch-live-counters">
          <div><strong>{props.total}</strong><span>Submitted</span></div>
          <div><strong>—</strong><span>Flagged</span></div>
          <div><strong>—</strong><span>Failed</span></div>
        </div>
      </section>
    );
  }

  if (props.error && !props.rows.length) {
    return (
      <section className="batch-results-panel batch-empty-results">
        <div className="batch-results-heading"><span>Batch failed</span><small>backend error</small></div>
        <div className="batch-request-error">
          <AlertTriangle size={28} />
          <strong>Batch could not be processed</strong>
          <p>{props.error}</p>
          <Button variant="secondary" onClick={props.onRetryFailed}><RotateCcw size={14} /> Retry</Button>
        </div>
      </section>
    );
  }

  if (!props.rows.length) {
    return (
      <section className="batch-results-panel batch-empty-results">
        <div className="batch-results-heading"><span>Results</span><small>awaiting run</small></div>
        <div><LoaderCircle size={28} /><strong>No results yet</strong><p>Validate the data, then run the batch. Each transaction result will appear here.</p></div>
      </section>
    );
  }

  return (
    <section className="batch-results-panel">
      <div className="batch-results-heading">
        <div><Check size={16} /><span>Batch completed</span></div>
        <Button variant="primary" size="sm" onClick={props.onExport}><Download size={14} /> Export</Button>
      </div>

      <div className="batch-summary-cards">
        <article><span>Total</span><strong>{props.total}</strong></article>
        <article><span>Processed</span><strong>{scoredRows.length}</strong></article>
        <article className="summary-flagged"><span>Flagged</span><strong>{props.flagged}</strong></article>
        <article className={props.failed ? "summary-failed" : ""}><span>Failed</span><strong>{props.failed}</strong></article>
        <article><span>Avg risk</span><strong>{averageRisk.toFixed(2)}</strong></article>
      </div>

      {props.failed ? (
        <div className="batch-partial-banner">
          <span><AlertTriangle size={15} /> The backend returned errors for {props.failed} rows.</span>
          <Button variant="ghost" size="sm" onClick={props.onRetryFailed}><RotateCcw size={13} /> Run again</Button>
        </div>
      ) : null}

      <div className="batch-result-filters">
        <label>Risk level
          <select value={props.riskFilter} onChange={(event) => props.onRiskFilterChange(event.target.value as BatchResultsProps["riskFilter"])}>
            <option value="ALL">All</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </label>
        <label className="batch-checkbox"><input type="checkbox" checked={props.flaggedOnly} onChange={(event) => props.onFlaggedOnlyChange(event.target.checked)} /> Flagged only</label>
        <span>{filteredRows.length} rows</span>
      </div>

      <div className="batch-table-scroll">
        <table className="batch-results-table">
          <thead><tr><th>#</th><th>Transaction</th><th>Amount</th><th>Channel</th><th>Risk</th><th>Flagged</th><th>Rules</th></tr></thead>
          <tbody>
            {filteredRows.map((row) => (
              <tr
                key={`${row.index}-${row.transaction.transaction_id}`}
                tabIndex={0}
                role="button"
                aria-label={`Open details for ${row.transaction.transaction_id}`}
                onClick={() => props.onOpen(row)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    props.onOpen(row);
                  }
                }}
              >
                <td>{row.index + 1}</td>
                <td><code title={row.transaction.transaction_id}>{row.transaction.transaction_id.slice(0, 10)}…</code><small>{row.transaction.sender_id.slice(0, 8)}…</small></td>
                <td>{formatAmount(row.transaction.amount, row.transaction.currency)}</td>
                <td><Badge>{row.transaction.channel}</Badge></td>
                {row.prediction ? (
                  <>
                    <td><strong>{row.prediction.risk_score.toFixed(2)}</strong><RiskBadge level={row.prediction.risk_level} /></td>
                    <td>{row.prediction.is_flagged ? <span className="flagged-check"><Check size={13} /> Yes</span> : "—"}</td>
                    <td><div className="rule-list-inline">{row.prediction.triggered_rules.map((rule) => <code key={rule.id}>{rule.id}</code>)}</div></td>
                  </>
                ) : (
                  <td colSpan={3}><span className="row-error">{row.error?.code}: {row.error?.message}</span></td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
