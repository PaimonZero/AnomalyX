import { useAuthToken } from "@/app/providers/auth-token-context";
import { useEffect, useRef, useState } from "react";
import { SlideFrame } from "./slide-frame";
import { SlideNavigation } from "./slide-navigation";
import { SlideProgress } from "./slide-progress";
import { useSlideshow } from "../hooks/use-slideshow";
import type { Slide } from "../types";

const HIDE_DELAY_MS = 3000;

interface SlideshowProps {
  slides: Slide[];
}

export function Slideshow({ slides }: SlideshowProps) {
  const { token } = useAuthToken();
  const {
    currentSlide,
    language,
    direction,
    isFullscreen,
    goNext,
    goPrev,
    goToSlide,
    toggleLanguage,
    toggleFullscreen,
  } = useSlideshow(slides.length);

  const [navVisible, setNavVisible] = useState(true);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Auto-hide nav after inactivity
  useEffect(() => {
    const scheduleHide = () => {
      setNavVisible(true);
      if (hideTimer.current) clearTimeout(hideTimer.current);
      hideTimer.current = setTimeout(() => setNavVisible(false), HIDE_DELAY_MS);
    };

    window.addEventListener("mousemove", scheduleHide);
    window.addEventListener("touchstart", scheduleHide);
    window.addEventListener("keydown", scheduleHide);

    // Start initial hide countdown
    hideTimer.current = setTimeout(() => setNavVisible(false), HIDE_DELAY_MS);

    return () => {
      window.removeEventListener("mousemove", scheduleHide);
      window.removeEventListener("touchstart", scheduleHide);
      window.removeEventListener("keydown", scheduleHide);
      if (hideTimer.current) clearTimeout(hideTimer.current);
    };
  }, []);

  const slide = slides[currentSlide];
  const DemoComponent = slide.demoComponent;
  const bgClass = slide.background ? `slide--${slide.background}` : "";

  return (
    <div className={`slideshow ${bgClass}`}>
      <SlideProgress current={currentSlide} total={slides.length} />

      <SlideFrame direction={direction} slideKey={`${slide.id}-${language}`}>
        <div className={`slide slide--${slide.layout}`}>
          {slide.content[language]}
          {DemoComponent && (
            <div className="slide-demo-area">
              <DemoComponent language={language} token={token} />
            </div>
          )}
        </div>
      </SlideFrame>

      <SlideNavigation
        current={currentSlide}
        total={slides.length}
        language={language}
        isFullscreen={isFullscreen}
        visible={navVisible}
        onPrev={goPrev}
        onNext={goNext}
        onGoTo={goToSlide}
        onToggleLanguage={toggleLanguage}
        onToggleFullscreen={toggleFullscreen}
      />
    </div>
  );
}
