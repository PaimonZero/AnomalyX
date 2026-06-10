create table if not exists public.alerts (
    id text primary key,
    transaction_id text not null,
    risk_score double precision not null check (risk_score >= 0 and risk_score <= 1),
    risk_level text not null check (risk_level in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
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

alter table public.alerts enable row level security;
alter table public.prediction_logs enable row level security;
alter table public.review_labels enable row level security;
