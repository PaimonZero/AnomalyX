import { Activity, Files, ShieldAlert, TerminalSquare } from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuthToken } from "@/app/providers/auth-token-context";

const navigation = [
  { to: "/alerts", label: "Alerts", icon: ShieldAlert },
  { to: "/api-testing", label: "Single Prediction", icon: TerminalSquare },
  { to: "/batch-scoring", label: "Predict Batch", icon: Files },
  { to: "/monitoring", label: "Monitoring", icon: Activity },
];

export function Sidebar() {
  const { customToken, envTokenConfigured, setCustomToken, setUseEnvToken, useEnvToken } = useAuthToken();

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">AX</span>
        <div>
          <strong>AnomalyX</strong>
        </div>
      </div>
      <nav aria-label="Main navigation">
        <p className="nav-label">Core demo</p>
        {navigation.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div>
          <strong>Bearer token</strong>
          <label className="switch-label sidebar-token-toggle">
            <input type="checkbox" checked={useEnvToken} onChange={(event) => setUseEnvToken(event.target.checked)} />
            <span /> Use .env token
          </label>
          <input
            className="sidebar-token-input"
            type="password"
            value={useEnvToken ? (envTokenConfigured ? "environment-token-configured" : "") : customToken}
            disabled={useEnvToken}
            onChange={(event) => setCustomToken(event.target.value)}
            placeholder={useEnvToken ? "VITE_API_TOKEN missing" : "Enter bearer token"}
          />
        </div>
      </div>
    </aside>
  );
}
