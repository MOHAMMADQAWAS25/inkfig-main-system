alter table public.exhibition_submissions
 add column withdrawal_status varchar(20),
 add column withdrawal_reason varchar(2000),
 add column withdrawal_requested_at timestamptz,
 add column withdrawal_review_reason varchar(2000),
 add column withdrawal_reviewer_user_id uuid references public.user_accounts(user_id),
 add column withdrawal_reviewed_at timestamptz,
 add constraint exhibition_withdrawal_status_check check (withdrawal_status in ('pending','rejected')),
 add constraint exhibition_withdrawal_reason_check check (
   withdrawal_status is null or (status='approved' and withdrawal_reason is not null and char_length(trim(withdrawal_reason)) > 0 and withdrawal_requested_at is not null)
 );
create index exhibition_withdrawal_pending_idx
 on public.exhibition_submissions(exhibition_id,withdrawal_requested_at,submission_id)
 where withdrawal_status='pending';
create table public.exhibition_withdrawal_audits (
 audit_id uuid primary key default gen_random_uuid(),
 exhibition_id uuid not null references public.exhibitions(exhibition_id) on delete cascade,
 submission_id uuid not null,
 work_id uuid references public.works(work_id) on delete set null,
 user_id uuid references public.user_accounts(user_id) on delete set null,
 reason varchar(2000) not null,
 decision varchar(20) not null check(decision in ('approved','rejected')),
 review_reason varchar(2000),
 reviewer_user_id uuid references public.user_accounts(user_id) on delete set null,
 reviewed_at timestamptz not null default now()
);
create index exhibition_withdrawal_audits_event_idx on public.exhibition_withdrawal_audits(exhibition_id,reviewed_at desc);
alter table public.exhibition_withdrawal_audits enable row level security;
revoke all on public.exhibition_withdrawal_audits from anon,authenticated;
grant select,insert on public.exhibition_withdrawal_audits to service_role;
-- Existing rows default to NULL; no data deleted/backfilled.
-- Rollback after withdrawing API/UI: export audit history before dropping the audit
-- table, index and added columns/constraints. Never discard pending requests silently.
