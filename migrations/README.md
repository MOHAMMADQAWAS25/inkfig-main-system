# Database migrations

Timestamped SQL and *_storage.py migrations already live here. The existing
`python -m migrations.run` runner orders filenames and tracks applied names in
public.schema_migrations. Set DATABASE_URL through approved secret configuration;
the runner converts postgresql+asyncpg:// for asyncpg. No local PostgreSQL is required.

Main depends on user-system schema/migrations; filenames must be globally distinct.
Never edit/rename an applied migration. Inspect every pending file and confirm
target/environment before an explicitly authorized manual run. Historical work-reset
SQL and storage-cleanup migrations are destructive; do not replay or remove their
ledger rows, run backfills or write production data as a documentation/test step.

Existing GitHub main deployment applies pending migrations and runs media backfill.
Explain/coordinate those effects before a production-triggering push. This setup
uses documentation-only [skip ci] commits instead. Migration/deployment/live state
must be reported separately from Git status. Storage and SQL are not a distributed
transaction; preserve failure/retry semantics rather than claim atomic deletion.
