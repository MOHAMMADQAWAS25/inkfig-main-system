-- Align indexes with the feed, profile, like, and save queries used by InkFig.
-- CONCURRENTLY is intentionally not used because the migration runner wraps each
-- migration in a transaction. These tables are still small at this project stage.

drop index if exists public.works_public_feed_idx;
drop index if exists public.works_owner_idx;
drop index if exists public.work_saves_user_created_idx;
drop index if exists public.work_links_work_order_idx;

create index if not exists works_published_feed_idx
    on public.works (created_at desc, work_id desc)
    where status = 'published';

create index if not exists works_published_type_feed_idx
    on public.works (type_id, created_at desc, work_id desc)
    where status = 'published';

create index if not exists works_published_owner_feed_idx
    on public.works (owner_user_id, created_at desc, work_id desc)
    where status = 'published';

create index if not exists work_likes_user_created_idx
    on public.work_likes (user_id, created_at desc, work_id desc);

create index if not exists work_saves_user_created_idx
    on public.work_saves (user_id, created_at desc, work_id desc);

-- work_links_work_position_unique already supplies the (work_id, position)
-- B-tree needed by ordered link aggregation, so no duplicate index is needed.

