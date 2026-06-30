import { Activity, ChevronLeft, ChevronRight, Files, ShieldAlert, TerminalSquare } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

import { useAuthToken } from "@/app/providers/auth-token-context";

const STORAGE_KEY = "anomalyx.sidebar.collapsed";
const COLLAPSED_WIDTH = 56;
const EXPANDED_WIDTH = 240;

function readCollapsed(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(STORAGE_KEY) === "true";
}

const navigation = [
  { to: "/alerts", label: "Alerts", icon: ShieldAlert },
  { to: "/api-testing", label: "Single Prediction", icon: TerminalSquare },
  { to: "/batch-scoring", label: "Predict Batch", icon: Files },
  { to: "/monitoring", label: "Monitoring", icon: Activity },
];

export function Sidebar() {
  const { customToken, setCustomToken } = useAuthToken();
  const [collapsed, setCollapsed] = useState(readCollapsed);

  const toggle = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      window.localStorage.setItem(STORAGE_KEY, String(next));
      return next;
    });
  }, []);

  useEffect(() => {
    const width = collapsed ? COLLAPSED_WIDTH : EXPANDED_WIDTH;
    document.documentElement.style.setProperty("--sidebar-width", `${width}px`);
  }, [collapsed]);

  return (
    <aside className={`sidebar${collapsed ? " sidebar--collapsed" : ""}`}>
      <div className="brand">
        <span className="brand-mark">AX</span>
        {!collapsed && (
          <div>
            <strong>AnomalyX</strong>
          </div>
        )}
      </div>

      <button
        type="button"
        className="sidebar-collapse-btn"
        onClick={toggle}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      <nav aria-label="Main navigation">
        {!collapsed && <p className="nav-label">Core demo</p>}
        {navigation.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} title={collapsed ? label : undefined}>
            <Icon size={18} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div>
            <label htmlFor="bearer-token-input">Bearer token</label>
            <input
              id="bearer-token-input"
              className="sidebar-token-input"
              type="password"
              value={customToken}
              onChange={(event) => setCustomToken(event.target.value)}
              placeholder="Enter bearer token"
            />
          </div>
        </div>
      )}
    </aside>
  );
}
