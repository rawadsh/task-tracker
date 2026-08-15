# Comments on Tasks — Feature Plan

## 1. Data Model

Add comment request/response models in `backend/app/models.py`, alongside `TaskCreate`, `TaskUpdate`, and `TaskResponse`.

Proposed models:

- A create-input model containing only `author` and `body`.
- A response model containing `id`, `task_id`, `author`, `body`, and `created_at`.

Follow the repository’s existing Pydantic conventions:

- Use `ConfigDict(extra="forbid")`, matching all current task models, so unexpected fields return `422`.
- Use field validators for author/body trimming and length constraints, as `TaskCreate`/`TaskUpdate` already do for title and tags.
- Require trimmed `author` to be 1–100 characters and trimmed `body` to be 1–2,000 characters.
- Do not accept `id`, `task_id`, or `created_at` from the client; storage generates those values.

Store comments separately from `TaskResponse`. The current task model represents task fields inline, while a comment is a distinct, repeatable record associated with a task. Adding a `comments` array to `TaskResponse` would change every existing task response shape, which `AGENTS.md` says not to do without explicit approval.

No new business rule is currently evident in `backend/app/business_rules.py`: author/body requirements are single-field validation, and task existence can be checked through storage. If later requirements introduce comment permissions or lifecycle rules, that would be the appropriate layer for them.

## 2. API Routes

Use task-scoped endpoints, consistent with the existing `/tasks/{task_id}` resource paths in `backend/app/main.py`.

### Create a comment

`POST /tasks/{task_id}/comments`

Request body:

- `author`: required string
- `body`: required string

Successful response:

- Status `201 Created`
- A comment response containing generated UUID `id`, the path’s `task_id`, normalized `author` and `body`, and a UTC `created_at` timestamp.

Errors:

- `404` if `task_id` does not identify an existing task, using the existing task-not-found detail convention: `Task with id {task_id} not found`.
- `422` for missing, blank, over-length, malformed, or unexpected fields.

### List a task’s comments

`GET /tasks/{task_id}/comments`

Successful response:

- Status `200 OK`
- A list of comment responses for that exact task.
- Return `[]` when the task exists but has no comments.

Errors:

- `404` if the task does not exist.

Recommended initial ordering: ascending `created_at` (oldest first), which suits a conversation-like history. This is a decision to confirm.

No standalone comment routes, edit route, or delete route are proposed in this initial scope. They are not required by the requested data shape and would introduce unresolved ownership and deletion decisions.

## 3. Tests

Create `backend/tests/test_comments.py`, following the feature-per-test-file organization already used by `test_due_dates.py` and `test_tags.py`.

Use the existing `client` and `created_task` fixtures from `backend/tests/conftest.py`. Its autouse storage reset should be extended through the storage reset implementation so comments do not leak between tests.

### Happy path

- `test_create_comment_returns_201_with_generated_fields`
- `test_create_comment_trims_author_and_body`
- `test_list_comments_for_task_returns_created_comments`
- `test_list_comments_for_task_with_no_comments_returns_200_empty_list`
- `test_comments_are_returned_oldest_first`

Assertions should follow current tests: check status codes, returned JSON values, and generated-field presence rather than hard-coding generated UUIDs/timestamps.

### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_at_max_length_succeeds`
- `test_create_comment_author_over_max_length_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_at_max_length_succeeds`
- `test_create_comment_body_over_max_length_returns_422`
- `test_create_comment_unknown_field_returns_422`

### Edge cases

- `test_create_comment_for_missing_task_returns_404`
- `test_list_comments_for_missing_task_returns_404`
- `test_list_comments_returns_only_requested_tasks_comments`
- `test_task_delete_comment_behavior_matches_approved_policy`

The final test name reflects a real unresolved lifecycle decision, so it should be finalized only after the cascade/retention policy is chosen.

## 4. Frontend Changes

Modify `frontend/index.html`, which is the repository’s single-file HTML/CSS/JavaScript frontend.

The current UI renders Kanban task cards and opens a task form modal for create/edit. It does not show a task-detail area or an existing comments UI. The least disruptive design is to extend the existing edit modal with a comments section for existing tasks:

- Add a “Comments” section when editing a task, not while creating one, because the task ID does not exist until creation succeeds.
- On opening the edit modal, request `GET /tasks/{task_id}/comments`.
- Render author, body, and `created_at` for each comment.
- Show a clear empty state for tasks with no comments.
- Add author and body inputs plus an “Add comment” action.
- Submit new comments to `POST /tasks/{task_id}/comments`.
- After a successful submission, reload the comment list and clear the comment form.
- Reuse the current error-display pattern (`formError` / `formatErrorMessage`) for server-side `422` and request failures.
- Escape comment author and body with the existing `escapeHtml()` helper before interpolation into HTML. This follows the current task-card handling and is especially important because comments are user-provided free text.

The task board’s `GET /tasks` request and task-card response rendering need not change if comments remain available only via the two new task-scoped endpoints.

## 5. Migration Notes

`backend/app/storage.py` currently persists tasks in a module-level `_tasks: dict[str, TaskResponse]`; the README confirms this state is in-memory and lost on process restart.

Add a separate in-memory comments structure keyed by comment ID, task ID, or both. A task-ID keyed collection is convenient for the proposed list endpoint; a comment-ID keyed collection is convenient if future standalone lookup/edit/delete routes are added. Either choice should preserve the existing task dictionary and existing `TaskResponse` shape.

Required storage responsibilities:

- Generate UUID4 strings and UTC timestamps, matching `add_task`.
- Confirm the parent task exists before creating or listing its comments.
- Return only comments belonging to the requested task.
- Clear comment state in `_reset()` alongside task state.

There is no database or durable data migration required for the current implementation because comments do not yet exist and all storage resets on restart. If a persistence layer is introduced later, enforce the task reference as a foreign key and decide its delete behavior explicitly.

## 6. Open Questions

1. When a task is deleted, should its comments be deleted, retained independently, or should task deletion be rejected while comments exist?
2. Should comments be immutable for this feature, or should the product support edit and delete actions later?
3. Is `author` intentionally anonymous/free text, or should it eventually reference an authenticated user? The repository currently has no authentication, as documented in `README.md`.
4. Should the comment list be oldest-first or newest-first?
5. Should comment bodies preserve leading/trailing whitespace, or should they be trimmed like task titles and tags? This plan recommends trimming, but the requirement only states length limits.
6. Should comments support plaintext only, or a limited formatting syntax? Plaintext is the safer initial scope given the current HTML-template frontend.
7. Should comments appear only inside the edit modal, or should task cards open a separate task-detail/comments view?

## Files read

- `AGENTS.md`
- `README.md`
- `backend/app/models.py`
- `backend/app/main.py`
- `backend/app/storage.py`
- `backend/app/business_rules.py`
- `backend/tests/conftest.py`
- `backend/tests/test_tasks.py`
- `backend/tests/test_due_dates.py`
- `backend/tests/test_tags.py`
- `frontend/index.html`
- `docs/midcourse/mini-adr.md`
- `docs/midcourse/user-stories.md`
- `docs/midcourse/verification.md`
- `docs/midcourse/prompt-log.md`

## Assumptions to verify

- Author and body should be trimmed before length validation and storage.
- A comment requires an existing task for both creation and listing.
- Comments should not be embedded in existing task response bodies.
- The initial feature is create-and-list only.
- Oldest-first ordering is desired.
- Comments should be removed when their parent task is deleted.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** The repo-grounded plan maps decisions to actual model, route, storage, test, and frontend conventions; the generic plan intentionally cannot.

**Plan I would hand to a teammate and why:** The repo-grounded plan, because it identifies affected files and protects existing response-shape and test-isolation conventions.

**A task shape where generic chat is enough:** Early product discovery or a greenfield prototype with no repository context yet.

**Where repo grounding mattered most:** Repository grounding mattered most in preserving TaskResponse compatibility, following the existing storage-reset and feature-test conventions, and placing comments in the actual edit-modal frontend flow
