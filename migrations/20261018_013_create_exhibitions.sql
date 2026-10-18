create table public.exhibitions (
 exhibition_id uuid primary key default gen_random_uuid(),
 creator_user_id uuid not null references public.user_accounts(user_id),
 name varchar(160) not null check (char_length(trim(name)) > 0),
 description text not null check (char_length(trim(description)) between 1 and 5000),
 event_at timestamptz not null,
 participation_opens_at timestamptz not null,
 participation_closes_at timestamptz not null,
 banner_path varchar(512),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 check (participation_opens_at < participation_closes_at),
 check (participation_closes_at <= event_at)
);
create index exhibitions_event_idx on public.exhibitions(event_at desc, exhibition_id desc);
create table public.exhibition_submissions (
 submission_id uuid primary key default gen_random_uuid(),
 exhibition_id uuid not null references public.exhibitions(exhibition_id) on delete cascade,
 work_id uuid not null references public.works(work_id) on delete cascade,
 user_id uuid not null references public.user_accounts(user_id) on delete cascade,
 status varchar(20) not null default 'pending' check (status in ('pending','approved','rejected')),
 rejection_reason varchar(2000),
 reviewer_user_id uuid references public.user_accounts(user_id),
 reviewed_at timestamptz,
 created_at timestamptz not null default now(),
 unique(exhibition_id,work_id),
 check (status <> 'rejected' or char_length(trim(rejection_reason)) > 0)
);
create index exhibition_submissions_queue_idx on public.exhibition_submissions(exhibition_id,status,created_at desc,submission_id desc);
create index exhibition_submissions_owner_idx on public.exhibition_submissions(exhibition_id,user_id,created_at desc);
create index exhibition_submissions_work_idx on public.exhibition_submissions(work_id);
create table public.exhibition_blocks (
 exhibition_id uuid not null references public.exhibitions(exhibition_id) on delete cascade,
 user_id uuid not null references public.user_accounts(user_id) on delete cascade,
 reason varchar(2000) not null check (char_length(trim(reason)) > 0),
 blocked_by uuid not null references public.user_accounts(user_id),
 created_at timestamptz not null default now(),
 primary key(exhibition_id,user_id)
);
insert into public.permissions(code,description) values
 ('exhibitions.manage','Create and manage all exhibitions and submissions'),
 ('exhibitions.participate','Submit owned works to exhibitions') on conflict do nothing;
insert into public.role_permissions(role_code,permission_code) values
 ('supervisor','exhibitions.manage'),('admin','exhibitions.manage'),('system_administrator','exhibitions.manage'),
 ('user','exhibitions.participate'),('supervisor','exhibitions.participate'),('admin','exhibitions.participate'),('system_administrator','exhibitions.participate') on conflict do nothing;
alter table public.exhibitions enable row level security;
alter table public.exhibition_submissions enable row level security;
alter table public.exhibition_blocks enable row level security;
revoke all on public.exhibitions,public.exhibition_submissions,public.exhibition_blocks from anon,authenticated;
grant select,insert,update,delete on public.exhibitions,public.exhibition_submissions,public.exhibition_blocks to service_role;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
 values('exhibition-banners','exhibition-banners',true,10485760,array['image/jpeg','image/png','image/webp']) on conflict(id) do nothing;
