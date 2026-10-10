# Infinite artwork feed: staged implementation

Stage 1 adds a new chronological card endpoint without changing the existing
`/works` or semantic-search response contracts. The frontend still uses those
older endpoints until its separately reviewed integration stage.

## API

`GET /api/v1/feed?limit=20&cursor=<opaque token>`

Optional `type_code` and `owner_user_id` filters preserve existing category and
artist scoping. The response is `{items, nextCursor, hasNextPage}`. Cards include
identity, artist, category labels, title, original image URL/MIME type, creation
time, and like/save state. Descriptions and external links are loaded from the
existing exact-artwork endpoint when opening details.

- Default page size: 20; maximum: 50. Invalid limits return FastAPI's existing 422.
- Malformed, unsupported, or filter-incompatible cursors return 400.
- An empty or final page has `nextCursor: null` and `hasNextPage: false`.
- A cursor belongs to its category and artist scope; clear it when either changes.
- Both guests and authenticated viewers retain existing published-work and
  active-owner visibility rules. Viewer interaction state is personalized.
- Responses use `Cache-Control: private, no-store` and vary by Cookie/Authorization.
- API Gateway throttles this specific production route at 20 requests/second
  with a burst of 40, shared across clients. It is not a per-user quota; local
  FastAPI does not enforce this infrastructure-level throttle.

## Cursor and query

The versioned URL-safe base64 token contains `(created_at, work_id)` and a filter
fingerprint. It is an opaque client continuation value, not an authorization
credential. The backend still checks visibility and binds all SQL values.

PostgreSQL orders by `created_at DESC, work_id DESC` and uses the strict tuple
comparison `(created_at, work_id) < (:created_at, :work_id)`. The ID tiebreaker
prevents equal timestamps from skipping posts. Inserting newer posts does not
shift the continuation boundary; a refresh starts a new feed. Deleting the cursor
post does not invalidate it because its sort values are encoded in the token.
This is a chronological continuation, not a frozen snapshot of edits/publications.

The bounded page is selected before calculating interactions. Existing migration
`20261006_005_optimize_query_indexes.sql` already creates the matching published
feed, category, and owner composite indexes; no duplicate migration is needed.

No clients, sockets, timestamps, or credentials are captured during module import.
Cursor decoding and repository operations run at request time for compatibility
with future AWS Lambda SnapStart adoption.

## Remaining review stages

2. Reusable abortable infinite-feed hook, retries, scroll preservation, and list
   layout; keep masonry as the system's default presentation.
3. Persist image dimensions, placeholders, and resized variants at publication;
   backfill existing works, then consume those fields with lazy responsive images.
   Preserve GIF animation and natural image proportions.
4. Precompute shortest-column masonry positions and preserve existing positions
   while appending, including RTL, resize, and device rotation.
5. Virtualize off-screen cards while retaining total scroll height.
6. Add behavior/performance coverage for the integrated hook, masonry, and media.

The image-only scope was confirmed by the user. No video pipeline is included.
Until stages 2–5 are integrated, this endpoint alone does not change the UI or
claim zero CLS, bounded DOM size, or measured 60fps scrolling. The existing
offset-based semantic search also needs separate cursor integration before it
can claim the same pagination guarantees as this chronological endpoint.

Run checks with `pytest -q` and `mypy src tests`. Pagination tests exercise
identical timestamps, inserts, deleted cursor posts, filter mismatch, and API
validation; repository tests verify the actual bound keyset query shape.
