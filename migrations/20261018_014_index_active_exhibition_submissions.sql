-- Supports eligibility and transaction-locked per-user participation quota checks.
-- No data is changed. Rollback: DROP INDEX public.exhibition_submissions_active_owner_idx;
create index exhibition_submissions_active_owner_idx
on public.exhibition_submissions(exhibition_id,user_id)
where status in ('pending','approved');
