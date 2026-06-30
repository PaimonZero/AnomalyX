import { useCallback, useEffect, useState } from "react";
import type { Language } from "../types";

export function useSlideshow(totalSlides: number) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [language, setLanguage] = useState<Language>("vi");
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [isFullscreen, setIsFullscreen] = useState(false);

  const goNext = useCallback(() => {
    if (currentSlide < totalSlides - 1) {
      setDirection("forward");
      setCurrentSlide((prev) => prev + 1);
    }
  }, [currentSlide, totalSlides]);

  const goPrev = useCallback(() => {
    if (currentSlide > 0) {
      setDirection("back");
      setCurrentSlide((prev) => prev - 1);
    }
  }, [currentSlide]);

  const goToSlide = useCallback(
    (index: number) => {
      if (index >= 0 && index < totalSlides) {
        setDirection(index > currentSlide ? "forward" : "back");
        setCurrentSlide(index);
      }
    },
    [currentSlide, totalSlides],
  );

  const toggleLanguage = useCallback(() => {
    setLanguage((prev) => (prev === "vi" ? "en" : "vi"));
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setIsFullscreen(false);
    }
  }, []);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        event.preventDefault();
        goNext();
      } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        event.preventDefault();
        goPrev();
      } else if (event.key === "l" || event.key === "L") {
        toggleLanguage();
      } else if (event.key === "f" || event.key === "F") {
        toggleFullscreen();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goNext, goPrev, toggleLanguage, toggleFullscreen]);

  return {
    currentSlide,
    language,
    direction,
    isFullscreen,
    goNext,
    goPrev,
    goToSlide,
    toggleLanguage,
    toggleFullscreen,
  };
}
