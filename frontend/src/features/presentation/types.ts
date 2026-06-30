import type { ReactNode } from "react";

export type Language = "vi" | "en";

export type SlideLayout = "title" | "content" | "two-column" | "demo" | "ending";

export interface SlideContent {
  vi: ReactNode;
  en: ReactNode;
}

export interface Slide {
  id: string;
  layout: SlideLayout;
  content: SlideContent;
  demoComponent?: React.FC<{ language: Language; token: string }>;
  background?: "default" | "accent" | "dark";
}
