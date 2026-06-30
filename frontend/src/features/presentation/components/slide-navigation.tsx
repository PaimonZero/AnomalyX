import { ChevronLeft, ChevronRight, Maximize2, Minimize2 } from "lucide-react";
import type { Language } from "../types";

interface SlideNavigationProps {
  current: number;
  total: number;
  language: Language;
  isFullscreen: boolean;
  visible: boolean;
  onPrev: () => void;
  onNext: () => void;
  onGoTo: (index: number) => void;
  onToggleLanguage: () => void;
  onToggleFullscreen: () => void;
}

export function SlideNavigation({
  current,
  total,
  language,
  isFullscreen,
  visible,
  onPrev,
  onNext,
  onGoTo,
  onToggleLanguage,
  onToggleFullscreen,
}: SlideNavigationProps) {
  return (
    <div className={`slide-nav${visible ? "" : " slide-nav--hidden"}`}>
      <button className="slide-nav-btn" type="button" onClick={onPrev} disabled={current === 0} aria-label="Previous slide">
        <ChevronLeft size={20} />
      </button>

      <div className="slide-nav-center">
        {Array.from({ length: total }).map((_, i) => (
          <button
            key={i}
            type="button"
            className={`slide-dot${i === current ? " slide-dot--active" : ""}`}
            onClick={() => onGoTo(i)}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
        <span className="slide-counter">
          {current + 1} / {total}
        </span>
      </div>

      <div className="slide-nav-right">
        <button
          className="slide-nav-btn slide-nav-lang"
          type="button"
          onClick={onToggleLanguage}
          aria-label="Toggle language"
        >
          {language === "vi" ? "EN" : "VI"}
        </button>
        <button
          className="slide-nav-btn"
          type="button"
          onClick={onToggleFullscreen}
          aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
        >
          {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
        </button>
        <button className="slide-nav-btn" type="button" onClick={onNext} disabled={current === total - 1} aria-label="Next slide">
          <ChevronRight size={20} />
        </button>
      </div>
    </div>
  );
}
