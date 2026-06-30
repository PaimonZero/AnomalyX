interface SlideProgressProps {
  current: number;
  total: number;
}

export function SlideProgress({ current, total }: SlideProgressProps) {
  const pct = ((current + 1) / total) * 100;

  return (
    <div className="slide-progress" role="progressbar" aria-valuenow={current + 1} aria-valuemin={1} aria-valuemax={total}>
      <div className="slide-progress-fill" style={{ width: `${pct}%` }} />
    </div>
  );
}
