# Infinite artwork feed: staged implementation

Stage 1 adds a new chronological card endpoint without changing the existing
`/works` or semantic-search pagination contracts. The main gallery now uses this
endpoint; ranked search and profile galleries retain their existing endpoints.

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

## Implemented image media and frontend stages

The frontend now integrates a cancellable TanStack infinite-query hook, retry,
list/masonry presentation, shortest-column placement, responsive lazy images,
bounded DOM virtualization, and navigation restoration. See its
`docs/infinite-feed.md` for tuning and tests.

Migration `20261011_012_add_work_media.sql` adds nullable `works.media` JSONB.
Cards, details, profile responses and search responses include optional `media`:
`{url,width,height,dominantColor,sizes:[{w,url}]}`. Dimensions are EXIF-normalized.
Publication validates actual image content and persists this metadata before
publishing, offloading Pillow CPU work to a request-time thread. Downloads are
capped at 10MiB and image headers at 80 million pixels, with a 25-million-pixel
decoded-canvas bound. JPEG decoder subsampling supports large originals without
allocating their full canvas; stored dimensions still describe the original.
Invalid images return
422; preparation/storage failures return 503 and may be retried while still draft.
Existing permissions and ownership checks remain unchanged.

Static images get WebP variants up to 236/474/736/1080px without upscaling.
Animated media keeps its original URL without static variants. Variants use
year-long cache headers; personalized card JSON remains private/no-store.
Deleting an artwork also deletes only its own derived variants. Originals are
never replaced by preparation/backfill.

Deploy schema and backend first. The deployment runs
`python -m scripts.backfill_work_media` with existing database/storage secrets
after health verification, then deploy the frontend. The additive backfill reads
25 missing records per batch, commits individually, and can safely be rerun;
failures remain eligible and make the backfill step fail visibly. It runs outside
Lambda rather than during feed requests. No new environment variables are needed.
All resources, clients and processing still initialize at execution/request time
for future SnapStart compatibility.

The image-only scope was confirmed by the user. No video pipeline is included.
The image-aware frontend reserves media geometry and bounds rendered cards.
It does not claim measured 60fps on physical phones or field-certified CLS. The existing
offset-based semantic search also needs separate cursor integration before it
can claim the same pagination guarantees as this chronological endpoint.

Run checks with `pytest -q` and `mypy src tests`. Pagination tests exercise
identical timestamps, inserts, deleted cursor posts, filter mismatch, and API
validation; repository tests verify the actual bound keyset query shape.
