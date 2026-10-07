create table if not exists public.work_deletion_audits (
    audit_id uuid primary key default gen_random_uuid(),
    work_id uuid not null,
    owner_user_id uuid not null,
    deleted_by_user_id uuid not null,
    reason text not null check (char_length(reason) between 10 and 1000),
    title varchar(160) not null,
    description text not null,
    type_id uuid not null,
    storage_bucket varchar(64) not null,
    storage_path varchar(512) not null,
    mime_type varchar(80) not null,
    deleted_at timestamptz not null default now()
);

create index if not exists work_deletion_audits_work_idx on public.work_deletion_audits(work_id);
create index if not exists work_deletion_audits_owner_time_idx on public.work_deletion_audits(owner_user_id, deleted_at desc);
create index if not exists work_deletion_audits_moderator_time_idx on public.work_deletion_audits(deleted_by_user_id, deleted_at desc);

alter table public.work_deletion_audits enable row level security;
revoke all on table public.work_deletion_audits from anon, authenticated;
grant select, insert on table public.work_deletion_audits to service_role;
