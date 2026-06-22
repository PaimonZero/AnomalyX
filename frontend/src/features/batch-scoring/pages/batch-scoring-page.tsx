import { CheckCircle2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { useHeaderAction } from "@/app/providers/header-action-context";
import { useAuthToken } from "@/app/providers/auth-token-context";
import { IntegrationSampleModal } from "@/features/api-testing/components/integration-sample-modal";
import { runBatch } from "@/features/batch-scoring/api/batch-api";
import { validateBatchJson } from "@/features/batch-scoring/api/batch-validation";
import { BatchDetailModal } from "@/features/batch-scoring/components/batch-detail-modal";
import { BatchInputPanel } from "@/features/batch-scoring/components/batch-input-panel";
import { BatchResults } from "@/features/batch-scoring/components/batch-results";
import { sampleBatchJson } from "@/features/batch-scoring/data/sample-batch";
import type { BatchResultRow } from "@/features/batch-scoring/types";
import { ApiError } from "@/shared/api/client";
import { env } from "@/shared/config/env";

export function BatchScoringPage() {
  const { token } = useAuthToken();
  const { setHeaderAction } = useHeaderAction();
  const [rawJson, setRawJson] = useState(sampleBatchJson);
  const [batchName, setBatchName] = useState("june-vip-review");
  const [outputFormat, setOutputFormat] = useState<"JSON" | "CSV">("JSON");
  const [running, setRunning] = useState(false);
  const [rows, setRows] = useState<BatchResultRow[]>([]);
  const [runError, setRunError] = useState<string | null>(null);
  const [progress, setProgress] = useState({ processed: 0, flagged: 0, failed: 0 });
  const [riskFilter, setRiskFilter] = useState<"ALL" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL">("ALL");
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [detailRow, setDetailRow] = useState<BatchResultRow | null>(null);
  const [integrationOpen, setIntegrationOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const validation = useMemo(() => validateBatchJson(rawJson), [rawJson]);
  const total = validation.transactions.length;
  const jsonValid = useMemo(() => {
    try {
      JSON.parse(rawJson);
      return true;
    } catch {
      return false;
    }
  }, [rawJson]);
  const integrationBody = useMemo(() => {
    let transactions: unknown[] = validation.transactions;

    try {
      const parsed = JSON.parse(rawJson);
      if (Array.isArray(parsed)) transactions = parsed;
    } catch {
      transactions = validation.transactions;
    }

    return JSON.stringify({
      batch_id: batchName || "batch-demo",
      transactions,
    }, null, 2);
  }, [batchName, rawJson, validation.transactions]);

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 2800);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    setHeaderAction(
      <span className="header-integration-hint">
        Want to integrate with another system?
        <button
          type="button"
          title="Show a cURL request sample for integrating batch scoring into another system."
          onClick={() => setIntegrationOpen(true)}
        >
          View cURL sample
        </button>
      </span>,
    );

    return () => setHeaderAction(null);
  }, [setHeaderAction]);

  const formatJson = () => {
    try {
      setRawJson(JSON.stringify(JSON.parse(rawJson), null, 2));
      setToast("JSON formatted.");
    } catch {
      setToast("Cannot format invalid JSON.");
    }
  };

  const run = async () => {
    if (validation.errors.length || !validation.transactions.length) return;

    const controller = new AbortController();
    abortRef.current = controller;
    setRunning(true);
    setRows([]);
    setRunError(null);
    setProgress({ processed: 0, flagged: 0, failed: 0 });

    try {
      const result = await runBatch(
        validation.transactions,
        batchName || `batch-${Date.now()}`,
        controller.signal,
        token,
      );
      const mappedRows = result.results.flatMap((item) => {
        const transaction = validation.transactions[item.index];
        if (!transaction) return [];
        return [{
          index: item.index,
          transaction,
          prediction: item.prediction ?? undefined,
          error: item.error ? { code: item.error.code, message: item.error.message } : undefined,
        } satisfies BatchResultRow];
      });
      setRows(mappedRows);
      setProgress({ processed: result.predictions.length, flagged: result.flagged_count, failed: result.errors.length });
      setToast(`Backend processed ${result.total_transactions} rows.`);
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") setToast("Batch cancelled.");
      else {
        const message = error instanceof ApiError ? `${error.code}: ${error.message}` : "Batch request failed.";
        setRunError(message);
        setToast(message);
      }
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  };

  const exportRows = () => {
    const scored = rows.map((row) => ({
      index: row.index,
      amount: row.transaction.amount,
      channel: row.transaction.channel,
      ...(row.prediction ?? { transaction_id: row.transaction.transaction_id, error: row.error }),
    }));
    const content = outputFormat === "JSON"
      ? JSON.stringify(scored, null, 2)
      : [
          "index,transaction_id,amount,channel,risk_score,risk_level,is_flagged",
          ...scored.map((row) => [
            row.index,
            row.transaction_id,
            row.amount,
            row.channel,
            "risk_score" in row ? row.risk_score : "",
            "risk_level" in row ? row.risk_level : "",
            "is_flagged" in row ? row.is_flagged : "",
          ].join(",")),
        ].join("\n");
    const blob = new Blob([content], { type: outputFormat === "JSON" ? "application/json" : "text/csv" });
    const link = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    link.href = objectUrl;
    link.download = `anomalyx_batch_${batchName || "untitled"}_${Date.now()}.${outputFormat.toLowerCase()}`;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
    setToast(`Exported ${outputFormat}.`);
  };

  const resultCounts = useMemo(
    () => ({
      flagged: rows.filter((row) => row.prediction?.is_flagged).length || progress.flagged,
      failed: rows.filter((row) => row.error).length || progress.failed,
    }),
    [progress.failed, progress.flagged, rows],
  );

  return (
    <div className="batch-page">
      <div className="batch-workspace">
        <BatchInputPanel
          rawJson={rawJson}
          batchName={batchName}
          outputFormat={outputFormat}
          validation={validation}
          jsonValid={jsonValid}
          running={running}
          onRawJsonChange={(value) => { setRawJson(value); setRows([]); setRunError(null); setProgress({ processed: 0, flagged: 0, failed: 0 }); }}
          onBatchNameChange={setBatchName}
          onOutputFormatChange={setOutputFormat}
          onLoadSample={() => { setRawJson(sampleBatchJson); setRows([]); setRunError(null); setProgress({ processed: 0, flagged: 0, failed: 0 }); }}
          onFormatJson={formatJson}
          onRun={() => void run()}
          onCancel={() => abortRef.current?.abort()}
        />
        <BatchResults
          rows={rows}
          error={runError}
          running={running}
          processed={progress.processed}
          total={total}
          flagged={resultCounts.flagged}
          failed={resultCounts.failed}
          riskFilter={riskFilter}
          flaggedOnly={flaggedOnly}
          onRiskFilterChange={setRiskFilter}
          onFlaggedOnlyChange={setFlaggedOnly}
          onOpen={setDetailRow}
          onExport={exportRows}
          onRetryFailed={() => void run()}
        />
      </div>

      <BatchDetailModal row={detailRow} batchName={batchName} onClose={() => setDetailRow(null)} />
      <IntegrationSampleModal
        apiBaseUrl={env.apiBaseUrl}
        body={integrationBody}
        description="Copy this cURL request into another service to run batch transaction scoring."
        endpointPath="/api/v1/batch-score"
        method="POST"
        open={integrationOpen}
        title="Batch integration sample"
        token={token}
        onClose={() => setIntegrationOpen(false)}
        onCopied={setToast}
      />
      {toast ? <div className="toast" role="status"><CheckCircle2 size={17} />{toast}</div> : null}
    </div>
  );
}
