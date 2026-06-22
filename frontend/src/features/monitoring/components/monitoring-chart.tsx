import type { MetricSeriesPoint } from "@/features/monitoring/types";
import { hasChartThreshold } from "@/features/monitoring/api/monitoring-display-format";

interface MonitoringChartProps {
  title: string;
  metric: string;
  points: MetricSeriesPoint[];
  valueLabel: string;
  threshold?: number;
}

export function MonitoringChart({ metric, points, threshold, title, valueLabel }: MonitoringChartProps) {
  const maximum = Math.max(...points.map((point) => point.value), threshold ?? 0, 1);

  return (
    <article className="monitor-chart-card">
      <header><div><h3>{title}</h3><code>{metric}</code></div><strong>{valueLabel}</strong></header>
      <div className="monitor-bar-chart" aria-label={title}>
        {points.map((point) => (
          <div key={point.label} title={`${point.label}: ${point.value}`}>
            <span style={{ height: `${Math.max((point.value / maximum) * 100, 5)}%` }} />
          </div>
        ))}
        {hasChartThreshold(threshold) ? <i style={{ bottom: `${(threshold / maximum) * 100}%` }}><small>{threshold}</small></i> : null}
      </div>
      <footer><span>{points[0]?.label}</span><span>{points.at(-1)?.label}</span></footer>
    </article>
  );
}
