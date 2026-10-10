alter table public.works add column if not exists media jsonb;
alter table public.works add constraint works_media_object
    check (media is null or jsonb_typeof(media) = 'object');
