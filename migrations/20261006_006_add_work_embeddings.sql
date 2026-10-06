create extension if not exists vector with schema extensions;

create table if not exists public.work_embeddings (
    work_id uuid primary key references public.works(work_id) on delete cascade,
    embedding extensions.vector(1024) not null,
    model_name varchar(100) not null,
    embedded_at timestamptz not null default now()
);

create index if not exists ix_work_embeddings_cosine
    on public.work_embeddings
    using hnsw (embedding extensions.vector_cosine_ops);
