import { RotateCcw, Search } from "lucide-react";

import type { AlertFilters } from "@/features/alerts/types";
import { Button } from "@/shared/ui/button";

interface AlertsToolbarProps {
  filters: AlertFilters;
  onChange: (filters: AlertFilters) => void;
  onClear: () => void;
}

export function AlertsToolbar({ filters, onChange, onClear }: AlertsToolbarProps) {
  const hasFilters = filters.search !== "" || filters.status !== "ALL" || filters.risk !== "ALL" || filters.source !== "ALL";

  return (
    <div className="alerts-toolbar">
      <label className="search-field">
        <Search size={15} aria-hidden="true" />
        <span className="sr-only">Search alerts</span>
        <input
          value={filters.search}
          onChange={(event) => onChange({ ...filters, search: event.target.value })}
          placeholder="Alert ID or Transaction ID"
        />
      </label>

      <label className="filter-field">
        <span>Status</span>
        <select value={filters.status} onChange={(event) => onChange({ ...filters, status: event.target.value as AlertFilters["status"] })}>
          <option value="ALL">All</option>
          <option value="NEW">New</option>
          <option value="ESCALATED">Escalated</option>
          <option value="DISMISSED">Dismissed</option>
        </select>
      </label>

      <label className="filter-field">
        <span>Risk level</span>
        <select value={filters.risk} onChange={(event) => onChange({ ...filters, risk: event.target.value as AlertFilters["risk"] })}>
          <option value="ALL">All</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
        </select>
      </label>

      <label className="filter-field">
        <span>Explanation</span>
        <select value={filters.source} onChange={(event) => onChange({ ...filters, source: event.target.value as AlertFilters["source"] })}>
          <option value="ALL">All</option>
          <option value="llm">LLM</option>
          <option value="template">Template</option>
          <option value="pending">Pending</option>
        </select>
      </label>

      <label className="filter-field filter-field--sort">
        <span>Sort</span>
        <select value={filters.sort} onChange={(event) => onChange({ ...filters, sort: event.target.value as AlertFilters["sort"] })}>
          <option value="risk_desc">Highest risk</option>
          <option value="updated_desc">Recently updated</option>
        </select>
      </label>

      <Button variant="ghost" size="sm" onClick={onClear} disabled={!hasFilters}>
        <RotateCcw size={14} />
        Clear filters
      </Button>
    </div>
  );
}
