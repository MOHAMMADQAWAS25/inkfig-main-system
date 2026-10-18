# Exhibitions

Exhibition management belongs to the main backend. Database permissions are checked
on every protected operation against the active, verified account and its current
role; stale JWT role claims cannot grant access. All supervisors, admins and system
administrators can manage every exhibition. Students can submit only their own
published works while participation is open and they are not blocked.

## API

- `GET /api/v1/exhibitions?limit=20&cursor=0&period=all|upcoming|past`: public
  listing. Upcoming exhibitions have `event_at > now()` and sort nearest first;
  past exhibitions have `event_at <= now()` and sort most recent first. Each period
  has its own continuation cursor. The default all preserves descending ordering.
- `POST /api/v1/exhibitions`: create; requires `exhibitions.manage`.
- `GET /api/v1/exhibitions/eligible?work_id={optional}&exhibition_id={optional}&cursor=0`:
  requires current `exhibitions.participate`; paginates only open, not-yet-started,
  unblocked exhibitions with capacity below ten active entries. Optional work must
  be owned and published; already-assigned works are excluded, including rejected
  entries. Optional exhibition ID supports targeted upload preflight.
- `GET /api/v1/exhibitions/{id}`: public details.
- `PUT /api/v1/exhibitions/{id}`: replace details; requires management.
- `POST /api/v1/exhibitions/{id}/submissions`: `{work_id}`, requires
  `exhibitions.participate`; returns 204 with a pending submission.
- `GET /api/v1/exhibitions/{id}/submissions?scope=public|mine|manage`: paginated;
  public returns only approved, published works from active, unblocked participants;
  mine requires participation permission, manage requires management permission.
  Optional `status=pending|approved|rejected` is applied before pagination without
  weakening scope. Each personal status section uses an independent cursor.
- `PATCH /api/v1/exhibitions/{id}/submissions/{submission_id}`:
  `{status: approved|rejected, reason?: string}`. Rejections require a reason.
- `POST /api/v1/exhibitions/{id}/submissions/{submission_id}/withdrawal`:
  owner-only, requires current participation permission. Body `{reason?: string}`.
  Pending memberships are removed immediately; approved memberships require a
  nonblank reason and become pending deletion requests without losing approval.
  Rejected memberships cannot be withdrawn. Missing/foreign membership404,
  missing approved-deletion reason422, duplicate request/invalid state409.
- `PATCH /api/v1/exhibitions/{id}/submissions/{submission_id}/withdrawal`:
  requires management, body `{status: approved|rejected, reason?: string}`.
  Approval removes membership only; rejection requires a reason and keeps the work
  approved. No pending request409. Both decisions preserve a separate audit record.
- `PUT /api/v1/exhibitions/{id}/blocks/{user_id}`: `{reason}`, blocks participation
  and hides all existing entries by this user from the public exhibition.
- `DELETE /api/v1/exhibitions/{id}/blocks/{user_id}`: permits participation again;
  previously approved entries become visible again.
- `GET /api/v1/exhibitions/{id}/blocks`: paginated management-only blocked list.
- `POST /api/v1/exhibitions/{id}/banner-uploads`: `{mime_type,file_size}` returns
  a scoped signed storage upload. JPEG/PNG/WebP, up to 10 MB.
- `POST /api/v1/exhibitions/{id}/banner-uploads/complete`: `{object_path}` verifies
  and processes the image before assigning it; deletes the preceding banner and
  its generated variants after replacement.

All dates must include a timezone. `participation_opens_at < participation_closes_at
<= event_at`; windows are inclusive at opening and exclusive at closing, checked
with database time. Lists default to 20 and cap at 50 with a numeric offset cursor.
Submission, review and block transactions lock the exhibition row to serialize
concurrent actions. Duplicate exhibition/work submissions return 409, missing work
or exhibition returns 404, insufficient permissions/blocked participation returns
403, closed windows return 409, invalid dates/reasons/images return 422, storage
failures return 503.

Existing and newly uploaded works remain normal publicly published profile works.
Public exhibition memberships are hidden until the scheduled event starts, enforced
by database time; private owner/review scopes remain available beforehand. Public
responses redact withdrawal request details.
Approval controls their exhibition membership only. Rejected entries retain their
reason for the owner and managers. A rejected work cannot be submitted twice to the
same exhibition; managers can reconsider its existing entry.

Both profile assignment and exhibition uploads submit exactly one work ID per
request. Each user may have at most ten pending or approved entries per exhibition;
rejection frees capacity. Submission insertion and rejected-entry reapproval check
this quota while holding the same exhibition row lock, preventing concurrent
requests from exceeding it. A full quota returns 409. Existing over-limit history
is not deleted; further submissions/reapprovals are refused until capacity returns.
Uploading still publishes a normal profile work, then submits its exhibition
membership; a failed membership request does not delete that profile work.
Owner deletion of an original profile work is blocked with409 while any approved
exhibition membership exists. The guard locks the work before any storage deletion,
and approval takes a compatible shared work lock to prevent concurrent bypass.
Existing moderator deletion privileges and their audited reasons remain unchanged.

## Deployment

Apply `20261018_013_create_exhibitions.sql` before deploying the main backend, then
deploy the frontend. No new environment variables or IAM privileges are needed.
For the assignment/quota release, also apply
`20261018_014_index_active_exhibition_submissions.sql`, which adds a partial index
on exhibition/user for pending and approved entries without changing existing data.
The record/withdrawal release also requires
`20261018_015_exhibition_withdrawal_requests.sql`: nullable withdrawal metadata,
pending-request index and RLS-protected decision audit history. Existing entries
remain unchanged. Do not drop these fields/table during rollback without exporting
history and handling outstanding requests first.
Rollback of that index is safe after withdrawing the new application behavior.
The migration adds three RLS-protected tables, indexed moderation/owner queues,
cascading submission/work relationships, role permission assignments and a public
`exhibition-banners` storage bucket with no direct client write policies.

Rollback requires withdrawing the new UI/API first; retain exhibition data and
banners unless explicitly approved for deletion. There is no destructive backfill.
Clients, clock reads and image processing are initialized/executed at request time
to preserve future SnapStart compatibility. This release does not add exhibition
WebSocket events. Banner cleanup is immediate; scheduled orphan cleanup is future
work if storage deletion fails after a successful banner assignment.

## Verification

`pytest` runs permission/validation tests. Opt in to the Supabase integration test
with `INKFIG_EXHIBITION_DB_TEST=1 pytest tests/test_exhibition_database.py` using a
configured `.env`; it creates temporary fixtures inside an explicitly rolled-back
transaction and performs no storage uploads or deletes.
