import { Moon, Sun } from "lucide-react";
import { useMemo, useState, type ReactNode } from "react";
import { Outlet, useLocation } from "react-router-dom";

import { HeaderActionContext } from "@/app/providers/header-action-context";
import { useTheme } from "@/app/providers/theme-context";
import { env } from "@/shared/config/env";
import { Sidebar } from "@/shared/ui/sidebar";

const pageTitles: Record<string, string> = {
  "/alerts": "Alert Queue",
  "/api-testing": "Single Prediction",
  "/batch-scoring": "Batch Scoring",
  "/monitoring": "Monitoring",
  "/presentation": "Presentation",
};

export function AppShell() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [headerAction, setHeaderAction] = useState<ReactNode>(null);
  const headerActionContextValue = useMemo(() => ({ setHeaderAction }), []);
  const pageTitle = pageTitles[location.pathname] ?? "AnomalyX";

  return (
    <HeaderActionContext.Provider value={headerActionContextValue}>
      <div className="app-shell">
        <Sidebar />
        <div className="app-workspace">
          <header className="app-header">
            <div className="header-title-group">
              <h1>{pageTitle}</h1>
              {headerAction}
            </div>
            <div className="header-actions">
              <span className="reviewer-badge">Reviewer: {env.reviewerId}</span>
              <button className="icon-button" type="button" onClick={toggleTheme} aria-label="Toggle light or dark theme">
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </header>
          <main className="app-content">
            <Outlet />
          </main>
        </div>
      </div>
    </HeaderActionContext.Provider>
  );
}
