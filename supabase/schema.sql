-- Supabase support is a legacy optional backend path. The FastAPI service uses
-- SUPABASE_SERVICE_ROLE_KEY, which bypasses RLS; no anon/authenticated client
-- policies are intended for this backend-only prototype.
--
-- Column names follow SupabaseAlertRepository's current REST contract. Some
-- names intentionally differ from backend/db/schema.sql, e.g. alerts.id and
-- review_labels.status, to avoid a repository-breaking schema migration.

create table if not exists public.alerts (
    id text primary key,
    transaction_id text not null,
    risk_score double precision not null check (risk_score >= 0 and risk_score <= 1),
    risk_level text not null check (risk_level in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    is_flagged boolean not null default true,
    status text not null check (status in ('NEW', 'DISMISSED', 'ESCALATED')),
    triggered_rules jsonb not null default '[]'::jsonb,
    top_features jsonb not null default '[]'::jsonb,
    explanation text,
    explanation_source text check (explanation_source is null or explanation_source in ('llm', 'template')),
    reviewer_id text,
    reviewed_at timestamptz,
    created_at timestamptz not null,
    updated_at timestamptz not null
);

create index if not exists idx_alerts_status_created_at
    on public.alerts (status, created_at desc);

create index if not exists idx_alerts_transaction_id
    on public.alerts (transaction_id);

create table if not exists public.prediction_logs (
    id bigint generated always as identity primary key,
    transaction_id text not null,
    risk_score double precision not null check (risk_score >= 0 and risk_score <= 1),
    risk_level text not null check (risk_level in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    is_flagged boolean not null,
    model_version text not null,
    triggered_rules jsonb not null default '[]'::jsonb,
    top_features jsonb not null default '[]'::jsonb,
    alert_id text references public.alerts(id),
    created_at timestamptz not null default now()
);

create index if not exists idx_prediction_logs_transaction_id
    on public.prediction_logs (transaction_id);

create table if not exists public.review_labels (
    id bigint generated always as identity primary key,
    alert_id text not null references public.alerts(id) on delete cascade,
    status text not null check (status in ('DISMISSED', 'ESCALATED')),
    reviewer_id text,
    created_at timestamptz not null default now()
);

create table if not exists public.feature_snapshots (
    snapshot_id uuid primary key default gen_random_uuid(),
    transaction_id text not null,
    features jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_feature_snapshots_transaction_id
    on public.feature_snapshots (transaction_id);

create table if not exists public.rule_versions (
    rule_version_id uuid primary key default gen_random_uuid(),
    version text not null,
    rules jsonb not null,
    is_active boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_rule_versions_active
    on public.rule_versions (is_active);

create table if not exists public.model_registry (
    model_id uuid primary key default gen_random_uuid(),
    model_version text not null unique,
    model_type text not null,
    metadata jsonb not null default '{}'::jsonb,
    is_active boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_model_registry_active
    on public.model_registry (is_active);

alter table public.alerts enable row level security;
alter table public.prediction_logs enable row level security;
alter table public.review_labels enable row level security;
alter table public.feature_snapshots enable row level security;
alter table public.rule_versions enable row level security;
alter table public.model_registry enable row level security;
