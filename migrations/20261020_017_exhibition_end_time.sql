-- Nullable for rolling-deploy/older-client compatibility; API resolves a missing
-- end to start + 24 hours. Existing schedules remain editable by managers.
alter table public.exhibitions add column event_ends_at timestamptz;
update public.exhibitions set event_ends_at=event_at+interval '24 hours';
alter table public.exhibitions add constraint exhibition_end_after_start
 check (event_ends_at is null or event_ends_at > event_at);
