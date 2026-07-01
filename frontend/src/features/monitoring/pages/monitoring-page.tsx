import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BellRing, CheckCircle2, Clock, RefreshCw, Server, ShieldCheck, Target } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuthToken } from "@/app/providers/auth-token-context";
import { useHeaderAction } from "@/app/providers/header-action-context";
import { formatHttpStatusBarWidth } from "@/features/monitoring/api/monitoring-display-format";
import { getRuleEngineDetails } from "@/features/monitoring/api/rules-detail";
import { formatReloadRulesSuccess } from "@/features/monitoring/api/rules-reload-format";
import { reloadRules } from "@/features/monitoring/api/rules-reload";
import { HealthStrip } from "@/features/monitoring/components/health-strip";
import { RuleEngineDetailModal } from "@/features/monitoring/components/rule-engine-detail-modal";
import { useMonitoring } from "@/features/monitoring/hooks/use-monitoring";
import { ApiError } from "@/shared/api/client";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

export function MonitoringPage() {
  const { token } = useAuthToken();
  const { setHeaderAction } = useHeaderAction();
  const [reloadConfirmOpen, setReloadConfirmOpen] = useState(false);
  const [reloadError, setReloadError] = useState<string | null>(null);
  const [reloadingRules, setReloadingRules] = useState(false);
  const [ruleDetailsOpen, setRuleDetailsOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const { health, metrics, refresh } = useMonitoring(false);
  const refreshMonitoring = useCallback(() => refresh(), [refresh]);
  const rulesQuery = useQuery({
    queryKey: ["monitoring", "rules", token],
    queryFn: () => getRuleEngineDetails(token),
    enabled: ruleDetailsOpen,
  });
  const data = metrics.data;
  const decisionTotal = useMemo(
    () => data ? Object.values(data.decisions).reduce((sum, value) => sum + value, 0) : 0,
    [data],
  );
  const riskScoreTotal = useMemo(
    () => data ? Object.values(data.riskScoreDistribution).reduce((sum, value) => sum + value, 0) : 0,
    [data],
  );
  const flaggedRate = data && decisionTotal
    ? ((data.decisions.HIGH + data.decisions.CRITICAL) / decisionTotal) * 100
    : 0;
  const explanationTotal = data ? data.explanationOutcomes.llm + data.explanationOutcomes.template : 0;
  const explanationSuccess = data && explanationTotal ? (data.explanationOutcomes.llm / explanationTotal) * 100 : 0;
  const loading = health.isLoading || metrics.isLoading;
  const failed = health.isError || metrics.isError;
  const maxRuleTrigger = data?.ruleTriggers[0]?.count ?? 0;

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 2800);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    setHeaderAction(
      <Button variant="secondary" size="sm" onClick={() => void refreshMonitoring()} disabled={health.isFetching || metrics.isFetching}>
        <RefreshCw size={14} className={health.isFetching || metrics.isFetching ? "spin" : ""} /> Refresh
      </Button>,
    );

    return () => setHeaderAction(null);
  }, [health.isFetching, metrics.isFetching, refreshMonitoring, setHeaderAction]);

  const confirmReloadRules = async () => {
    setReloadingRules(true);
    setReloadError(null);

    try {
      const result = await reloadRules(token);
      setReloadConfirmOpen(false);
      setToast(formatReloadRulesSuccess(result));
      await rulesQuery.refetch();
      await refreshMonitoring();
    } catch (error) {
      const message = error instanceof ApiError
        ? `${error.code}: ${error.message}`
        : "Could not reload rules. Check bearer token or backend status.";
      setReloadError(message);
    } finally {
      setReloadingRules(false);
    }
  };

  return (
    <div className="monitoring-page">
      {failed ? (
        <div className="alerts-error" role="alert"><div><AlertTriangle size={17} /><span>Could not load monitoring data from the backend.</span></div><Button size="sm" onClick={() => void refreshMonitoring()}>Retry</Button></div>
      ) : null}

      {loading || !health.data || !data ? (
        <div className="monitor-loading" role="status">Loading monitoring data…</div>
      ) : (
        <>
          <HealthStrip
            health={health.data}
            onOpenRuleDetails={() => setRuleDetailsOpen(true)}
          />

          <section className="monitor-kpis">
            <article><div className="monitor-kpi-icon"><Server size={17} /></div><span>HTTP requests</span><strong>{data.requestsTotal.toLocaleString("en-US")}</strong><small>{data.requestSuccessRate}% successful</small></article>
            <article><div className="monitor-kpi-icon"><Clock size={17} /></div><span>Prediction p95</span><strong>{data.predictionP95Ms}<em>ms</em></strong><small>Predict + batch endpoint latency</small></article>
            <article><div className="monitor-kpi-icon"><BellRing size={17} /></div><span>Alerts created</span><strong>{data.alertsTotal}</strong><small>{flaggedRate.toFixed(1)}% decisions flagged</small></article>
            <article><div className="monitor-kpi-icon"><Target size={17} /></div><span>Flagged rate</span><strong>{flaggedRate.toFixed(1)}<em>%</em></strong><small>{data.alertsTotal} flagged of {decisionTotal} decisions</small></article>
            <article><div className="monitor-kpi-icon"><ShieldCheck size={17} /></div><span>LLM outcomes</span><strong>{explanationSuccess.toFixed(1)}<em>%</em></strong><small>{data.fallbackTotal} template fallback</small></article>
          </section>

          <section className="monitor-section">
            <div className="monitor-section-heading"><div><Activity size={16} /><h2>Runtime metrics</h2></div><span>Prometheus · live snapshot</span></div>
            <div className="monitor-chart-grid">
              <article className="monitor-chart-card">
                <header><div><h3>Decision distribution</h3><code>anomalyx_decisions_total</code></div><strong>{decisionTotal.toLocaleString("en-US")}</strong></header>
                <div className="decision-stack">
                  {Object.entries(data.decisions).map(([level, value]) => <span key={level} className={`decision-${level.toLowerCase()}`} style={{ width: `${decisionTotal ? (value / decisionTotal) * 100 : 0}%` }} title={`${level}: ${value}`} />)}
                </div>
                <div className="decision-legend">
                  {Object.entries(data.decisions).map(([level, value]) => <div key={level}><i className={`decision-${level.toLowerCase()}`} /><span>{level}</span><strong>{value}</strong></div>)}
                </div>
              </article>

              <article className="monitor-chart-card">
                <header><div><h3>HTTP status</h3><code>status_code label</code></div><strong>{data.requestSuccessRate}%</strong></header>
                <div className="status-bars">
                  {Object.entries(data.httpStatuses).map(([status, value]) => <div key={status}><span>{status}</span><div><i className={`status-${status[0]}`} style={{ width: formatHttpStatusBarWidth(value, data.requestsTotal) }} /></div><strong>{value}</strong></div>)}
                </div>
              </article>

              <article className="monitor-chart-card">
                <header><div><h3>Risk score distribution</h3><code>anomalyx_prediction_risk_score_bucket</code></div><strong>{riskScoreTotal.toLocaleString("en-US")}</strong></header>
                <div className="risk-score-stack">
                  {Object.entries(data.riskScoreDistribution).map(([level, value]) => <span key={level} className={`risk-score-${level.toLowerCase()}`} style={{ width: `${riskScoreTotal ? (value / riskScoreTotal) * 100 : 0}%` }} title={`${level}: ${value}`} />)}
                </div>
                <div className="decision-legend">
                  {Object.entries(data.riskScoreDistribution).map(([level, value]) => <div key={level}><i className={`risk-score-${level.toLowerCase()}`} /><span>{level}</span><strong>{value}</strong></div>)}
                </div>
              </article>
            </div>
          </section>

          <section className="monitor-lower-grid">
            <article className="monitor-panel">
              <header><div><Activity size={17} /><h2>Rule triggers</h2></div><span>{data.ruleTriggers.reduce((sum, rule) => sum + rule.count, 0).toLocaleString("en-US")}</span></header>
              <div className="rule-trigger-bars">
                {data.ruleTriggers.length
                  ? data.ruleTriggers.map((rule) => <div key={rule.id}><code>{rule.id}</code><div><span style={{ width: `${maxRuleTrigger ? (rule.count / maxRuleTrigger) * 100 : 0}%` }} /></div><strong>{rule.count}</strong></div>)
                  : <p className="monitor-empty">No rules have been triggered yet.</p>}
              </div>
            </article>

            <article className="monitor-panel">
              <header><div><ShieldCheck size={17} /><h2>LLM explanations</h2></div><span>p95 {data.explanationP95Ms}ms</span></header>
              <div className="llm-outcomes">
                <div><span>LLM</span><strong>{data.explanationOutcomes.llm}</strong><small>{explanationSuccess.toFixed(1)}%</small></div>
                <div><span>Template</span><strong>{data.explanationOutcomes.template}</strong><small>{(100 - explanationSuccess).toFixed(1)}%</small></div>
              </div>
            </article>
          </section>
        </>
      )}

      <RuleEngineDetailModal
        details={rulesQuery.data}
        error={rulesQuery.error instanceof Error ? rulesQuery.error.message : null}
        loading={rulesQuery.isLoading || rulesQuery.isFetching}
        open={ruleDetailsOpen}
        reloadingRules={reloadingRules}
        onClose={() => setRuleDetailsOpen(false)}
        onReloadRules={() => {
          setReloadError(null);
          setReloadConfirmOpen(true);
        }}
        onRetry={() => void rulesQuery.refetch()}
      />

      <Modal
        open={reloadConfirmOpen}
        onClose={() => {
          if (!reloadingRules) setReloadConfirmOpen(false);
        }}
        title="Apply rules.yaml to backend?"
        description="Confirm before the backend loads the latest rules.yaml configuration."
      >
        <div className="confirm-form">
          <p>
            If you changed rules.yaml, the backend will load the latest rule configuration. New single prediction and batch scoring requests will use the updated rules.
          </p>
          {reloadError ? <div className="confirm-error" role="alert">{reloadError}</div> : null}
          <div className="confirm-actions">
            <Button variant="secondary" disabled={reloadingRules} onClick={() => setReloadConfirmOpen(false)}>Cancel</Button>
            <Button variant="primary" disabled={reloadingRules} onClick={() => void confirmReloadRules()}>
              {reloadingRules ? "Applying rules to backend…" : "Apply rules.yaml to backend"}
            </Button>
          </div>
        </div>
      </Modal>

      {toast ? <div className="toast" role="status"><CheckCircle2 size={17} />{toast}</div> : null}
    </div>
  );
}

