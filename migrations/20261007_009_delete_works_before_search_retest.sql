-- One-time reset requested before validating resized semantic-image embeddings.
-- Related links, likes, saves, and embeddings are removed by ON DELETE CASCADE.
delete from public.works;
