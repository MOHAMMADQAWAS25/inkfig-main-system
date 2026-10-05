create table if not exists public.work_saves (
    work_id uuid not null references public.works(work_id) on delete cascade,
    user_id uuid not null,
    created_at timestamptz not null default now(),
    primary key (work_id, user_id)
);

create index if not exists work_saves_user_created_idx
    on public.work_saves(user_id, created_at desc);

alter table public.work_saves enable row level security;
revoke all on public.work_saves from anon, authenticated;
grant select, insert, delete on public.work_saves to service_role;
