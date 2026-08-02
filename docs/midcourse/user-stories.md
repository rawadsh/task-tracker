# User Stories

## Feature 1 — Due Dates + Overdue Filter

### US-D01
**As a team member, I want to optionally set a due date when creating a task so that I only track deadlines for tasks that actually need one.**

Acceptance Criteria:
1. `POST /tasks` accepts an optional `due_date` in `YYYY-MM-DD` format.
2. Omitting `due_date` succeeds and returns `due_date: null`.
3. A malformed `due_date` (e.g. non-date string) returns `422`.

Notes/Assumptions:
- No default due date is assumed — stays fully optional per approved decision.

### US-D02
**As a team member, I want to change or remove a task's due date through PATCH so that I can correct or clear deadlines as plans change.**

Acceptance Criteria:
1. `PATCH /tasks/{id}` with a new `due_date` updates it and leaves other fields untouched.
2. `PATCH` with `due_date: null` explicitly clears an existing due date.
3. `PATCH` with an invalid `due_date` returns `422` and leaves the task unmodified.

Notes/Assumptions:
- Uses the existing `exclude_unset` PATCH pattern already in `storage.py`, so omitting the field entirely (vs. sending `null`) is distinguishable without new logic.

### US-D03
**As a team member, I want overdue tasks to be identified consistently so that I can quickly recognize unfinished work that has passed its deadline.**

Acceptance Criteria:
1. `ToDo` or `InProgress` with `due_date` before today → overdue.
2. `Done` with `due_date` before today → NOT overdue.
3. No `due_date` → NOT overdue, regardless of status.

Notes/Assumptions:
- **AI assumption corrected:** an earlier draft assumed the overdue query filter should also support `overdue=false` as a symmetric boolean toggle. This was corrected and rejected — only `overdue=true` is in scope; no `overdue=false` filtering is implemented.

### US-D04
**As a team member, I want to filter the task list to only overdue tasks so that I can quickly find what needs attention.**

Acceptance Criteria:
1. `GET /tasks?overdue=true` returns only tasks matching the US-D03 overdue definition.
2. `GET /tasks?overdue=true` returns `200` with `[]` when no tasks are overdue.
3. `GET /tasks` without the `overdue` param is unaffected — existing `status`/`priority` filtering still works unchanged.

Notes/Assumptions:
- `overdue=false` is explicitly out of scope per the corrected assumption in US-D03 — not implementing it, not stubbing it.

### US-D05
**As a team member, I want to see due dates and overdue status on tasks in the UI so that I can tell what's coming due or already late without opening each task.**

Acceptance Criteria:
1. A task's due date is shown on its card/detail view when set.
2. A task the backend marks `overdue: true` shows a distinct visual indicator.
3. A task with no due date shows neither a date nor an overdue indicator.

Notes/Assumptions:
- Frontend renders the backend's `overdue` value as-is; JS may translate a `422` into a friendly message but does not recompute overdue logic itself.

## Feature 2 — Tags/Labels

### US-T01
**As a team member, I want to attach free-text tags to a task when creating it so that I can categorize work without a rigid category list.**

Acceptance Criteria:
1. `POST /tasks` accepts an optional `tags: list[str]`.
2. Omitting `tags` succeeds and returns `tags: []`.
3. Each tag is trimmed of leading/trailing whitespace before storage.
4. A blank tag (empty string, or whitespace-only) is rejected with `422`.

Notes/Assumptions:
- **Decision:** omitted `tags` defaults to `[]` (not `null`) — approved.

### US-T02
**As a team member, I want a bounded number of tags per task, each with a bounded length, so that tags stay usable as short labels rather than becoming free-form text dumps.**

Acceptance Criteria:
1. Creating or updating a task with more than 10 tags returns `422`.
2. Creating or updating a task with any single tag longer than 30 characters returns `422`.
3. A task with exactly 10 tags, or a tag of exactly 30 characters, succeeds.

Notes/Assumptions:
- **Decision:** maximum 10 tags per task, maximum 30 characters per tag — approved as explicit hard limits for Feature 2.

### US-T03
**As a team member, I want to change a task's tags through PATCH so that I can re-categorize a task as work evolves.**

Acceptance Criteria:
1. `PATCH /tasks/{id}` with a new `tags` list replaces the entire existing list (not merged/appended).
2. `PATCH` with `tags: []` clears all tags.
3. `PATCH` with an invalid tag (blank, over-length, or over-count) returns `422` and leaves the task unmodified.

Notes/Assumptions:
- **Decision:** full-replacement semantics — approved. `tags: []` clears all tags; an omitted `tags` field preserves the existing list unchanged (same `exclude_unset` pattern as `due_date`, US-D02).

### US-T04
**As a team member, I want to filter the task list by tag so that I can quickly find all tasks under a given label.**

Acceptance Criteria:
1. `GET /tasks?tag=<value>` returns only tasks whose `tags` list contains an exact match for `<value>`.
2. `GET /tasks?tag=<value>` returns `200` with `[]` when no tasks have that tag.
3. `GET /tasks` without the `tag` param is unaffected — existing `status`/`priority`/`overdue` filtering still works unchanged.

Notes/Assumptions:
- **Decision:** single-tag, exact-match, case-sensitive filtering only — approved. No multi-tag AND/OR filtering in scope.

### US-T05
**As a team member, I want to enter and see tags in the UI so that I can label tasks and filter the board by tag without using the API directly.**

Acceptance Criteria:
1. The task form has a tag input (comma-separated entry) that produces a `tags` list on submit.
2. Each task card displays its tags as chips.
3. A tag filter control lets me narrow the visible task list to one tag at a time, using the same `GET /tasks?tag=...` the backend exposes.
4. A task with no tags shows no chips (no empty/placeholder chip).

Notes/Assumptions:
- Approved as proposed. Frontend sends/receives tags exactly as backend-validated strings — no client-side trimming/validation duplicated, consistent with the due-date frontend approach (US-D05).