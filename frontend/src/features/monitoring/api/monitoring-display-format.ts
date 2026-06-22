export function formatHttpStatusBarWidth(value: number, requestsTotal: number) {
  return `${requestsTotal ? (value / requestsTotal) * 100 : 0}%`;
}
