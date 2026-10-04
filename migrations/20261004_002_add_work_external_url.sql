alter table public.works
    add column if not exists external_url varchar(2083);

alter table public.works
    drop constraint if exists works_external_url_http_check;

alter table public.works
    add constraint works_external_url_http_check
    check (external_url is null or external_url ~* '^https?://');
