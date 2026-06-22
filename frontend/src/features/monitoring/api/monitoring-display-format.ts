export function formatHttpStatusBarWidth(value: number, requestsTotal: number) {
  return `${requestsTotal ? (value / requestsTotal) * 100 : 0}%`;
}

export function hasChartThreshold(threshold: number | null | undefined): threshold is number {
  return threshold != null;
}
