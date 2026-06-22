import { useCallback, useEffect, useMemo, useState, type PropsWithChildren } from "react";

import { ThemeContext, type Theme } from "@/app/providers/theme-context";
import { applyTheme, getInitialTheme } from "@/app/providers/theme-utils";

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }, []);

  const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
