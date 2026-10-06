-- One-time reset requested before semantic artwork indexing goes into use.
-- Related links, likes, saves, and embeddings are removed by ON DELETE CASCADE.
delete from public.works;
