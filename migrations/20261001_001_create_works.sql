create extension if not exists pgcrypto;
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('works', 'works', true, 10485760, array['image/jpeg','image/png','image/webp','image/gif'])
on conflict (id) do update set public=true, file_size_limit=excluded.file_size_limit, allowed_mime_types=excluded.allowed_mime_types;
create table if not exists public.work_types (
 type_id uuid primary key default gen_random_uuid(), code varchar(64) not null unique,
 name_en varchar(120) not null, name_ar varchar(120) not null, is_active boolean not null default true,
 created_at timestamptz not null default now()
);
create table if not exists public.works (
 work_id uuid primary key, owner_user_id uuid not null references public.user_accounts(user_id) on delete cascade,
 type_id uuid not null references public.work_types(type_id), title varchar(160) not null,
 description text not null default '', storage_bucket varchar(64) not null default 'works', storage_path varchar(512) not null unique,
 mime_type varchar(80) not null, file_size bigint not null check(file_size>0 and file_size<=10485760),
 status varchar(20) not null default 'draft' check(status in ('draft','published','archived')),
 created_at timestamptz not null default now(), published_at timestamptz
);
create index if not exists works_public_feed_idx on public.works(published_at desc, work_id) where status='published';
create index if not exists works_owner_idx on public.works(owner_user_id, created_at desc);
create table if not exists public.work_likes (
 work_id uuid not null references public.works(work_id) on delete cascade,
 user_id uuid not null references public.user_accounts(user_id) on delete cascade,
 created_at timestamptz not null default now(), primary key(work_id,user_id)
);
alter table public.work_types enable row level security; alter table public.works enable row level security; alter table public.work_likes enable row level security;
revoke all on public.work_types, public.works, public.work_likes from anon, authenticated;
grant select,insert,update,delete on public.work_types, public.works, public.work_likes to service_role;
