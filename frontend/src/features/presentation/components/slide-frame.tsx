import type { ReactNode } from "react";

interface SlideFrameProps {
  children: ReactNode;
  direction: "forward" | "back";
  slideKey: string;
}

export function SlideFrame({ children, direction, slideKey }: SlideFrameProps) {
  const enterClass = direction === "forward" ? "slide-enter-forward" : "slide-enter-back";

  return (
    <div className="slide-frame" key={slideKey}>
      <div className={enterClass}>{children}</div>
    </div>
  );
}
