create extension if not exists pgcrypto;

create table if not exists alerts (
    alert_id text primary key,
    transaction_id text not null,
    risk_score double precision not null check (risk_score >= 0 and risk_score <= 1),
    risk_level text not null check (risk_level in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    is_flagged boolean not null default true,
    triggered_rules jsonb not null default '[]'::jsonb,
    top_features jsonb not null default '[]'::jsonb,
    explanation text,
    explanation_source text check (explanation_source is null or explanation_source in ('llm', 'template')),
    status text not null check (status in ('NEW', 'DISMISSED', 'ESCALATED')),
    reviewer_id text,
    reviewed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_alerts_transaction_id on alerts (transaction_id);
create index if not exists idx_alerts_status on alerts (status);
create index if not exists idx_alerts_created_at on alerts (created_at desc);

create table if not exists review_labels (
    label_id uuid primary key default gen_random_uuid(),
    alert_id text not null references alerts(alert_id) on delete cascade,
    transaction_id text not null,
    label text not null check (label in ('DISMISSED', 'ESCALATED')),
    reviewer_id text,
    created_at timestamptz not null default now()
);

create index if not exists idx_review_labels_alert_id on review_labels (alert_id);

create table if not exists prediction_logs (
    prediction_id uuid primary key default gen_random_uuid(),
    transaction_id text not null,
    risk_score double precision not null check (risk_score >= 0 and risk_score <= 1),
    risk_level text not null check (risk_level in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    is_flagged boolean not null,
    model_version text not null,
    triggered_rules jsonb not null default '[]'::jsonb,
    top_features jsonb not null default '[]'::jsonb,
    alert_id text references alerts(alert_id),
    created_at timestamptz not null default now()
);

create index if not exists idx_prediction_logs_transaction_id on prediction_logs (transaction_id);
create index if not exists idx_prediction_logs_created_at on prediction_logs (created_at desc);

create table if not exists feature_snapshots (
    snapshot_id uuid primary key default gen_random_uuid(),
    transaction_id text not null,
    features jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_feature_snapshots_transaction_id on feature_snapshots (transaction_id);

create table if not exists rule_versions (
    rule_version_id uuid primary key default gen_random_uuid(),
    version text not null,
    rules jsonb not null,
    is_active boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_rule_versions_active on rule_versions (is_active);

create table if not exists model_registry (
    model_id uuid primary key default gen_random_uuid(),
    model_version text not null unique,
    model_type text not null,
    metadata jsonb not null default '{}'::jsonb,
    is_active boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_model_registry_active on model_registry (is_active);
