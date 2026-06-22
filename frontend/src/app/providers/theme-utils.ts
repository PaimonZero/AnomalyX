import type { Theme } from "@/app/providers/theme-context";

export const THEME_STORAGE_KEY = "anomalyx-theme";

const THEME_COLORS: Record<Theme, string> = {
  dark: "#0d0f17",
  light: "#f5f4ef",
};

interface InitialThemeRuntime {
  storage?: Pick<Storage, "getItem">;
  prefersLight?: () => boolean;
}

interface ApplyThemeRuntime {
  document?: Document;
  storage?: Pick<Storage, "setItem">;
}

export function getThemeColor(theme: Theme) {
  return THEME_COLORS[theme];
}

export function getInitialTheme(runtime: InitialThemeRuntime = {}): Theme {
  const storage = runtime.storage ?? localStorage;
  const prefersLight = runtime.prefersLight ?? (() => window.matchMedia("(prefers-color-scheme: light)").matches);
  const storedTheme = storage.getItem(THEME_STORAGE_KEY);
  if (storedTheme === "dark" || storedTheme === "light") return storedTheme;
  return prefersLight() ? "light" : "dark";
}

export function applyTheme(theme: Theme, runtime: ApplyThemeRuntime = {}) {
  const targetDocument = runtime.document ?? document;
  const storage = runtime.storage ?? localStorage;
  targetDocument.documentElement.dataset.theme = theme;
  storage.setItem(THEME_STORAGE_KEY, theme);
  const themeColor = targetDocument.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  if (themeColor) themeColor.content = getThemeColor(theme);
}
