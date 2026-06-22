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
  const { customToken, setCustomToken } = useAuthToken();

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
    </aside>
  );
}
