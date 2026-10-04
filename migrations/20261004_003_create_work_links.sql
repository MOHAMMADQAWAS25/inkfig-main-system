create table if not exists public.work_links (
    link_id uuid primary key default gen_random_uuid(),
    work_id uuid not null references public.works(work_id) on delete cascade,
    url varchar(2083) not null,
    label varchar(120),
    position smallint not null check (position >= 0 and position < 10),
    created_at timestamptz not null default now(),
    constraint work_links_http_url_check check (url ~* '^https?://'),
    constraint work_links_work_url_unique unique (work_id, url),
    constraint work_links_work_position_unique unique (work_id, position)
);

insert into public.work_links (work_id, url, position)
select work_id, external_url, 0 from public.works
where external_url is not null
on conflict (work_id, url) do nothing;

alter table public.works drop constraint if exists works_external_url_http_check;
alter table public.works drop column if exists external_url;

create index if not exists work_links_work_order_idx
    on public.work_links(work_id, position);

alter table public.work_links enable row level security;
revoke all on public.work_links from anon, authenticated;
grant select, insert, update, delete on public.work_links to service_role;
