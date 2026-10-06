-- Second one-time artwork reset explicitly requested after semantic-search testing.
-- Related links, likes, saves, and embeddings are removed by ON DELETE CASCADE.
delete from public.works;
