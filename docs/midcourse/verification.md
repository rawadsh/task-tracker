# Verification

## Baseline (before feature work)

**Branch:** `mid-course-project`

### Servers started manually
- Backend: `uvicorn app.main:app --reload --port 8000` — started clean.
- Frontend: `python -m http.server 5500` — served `frontend/` on port 5500.

### Backend test suite
Command: `pytest tests/ -v`, run from `backend/` with venv active.

Result: **19 passed, 3 warnings in 0.40s** — all green`.

Warnings (pre-existing, not addressed here): `httpx`-via-`starlette.testclient` deprecation; `HTTP_422_UNPROCESSABLE_ENTITY` deprecated in favor of `HTTP_422_UNPROCESSABLE_CONTENT`.

Full transcript:
```
(venv) PS ...\backend> uvicorn app.main:app --reload --port 8000
INFO:     Will watch for changes in these directories: ['...\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [36976] using WatchFiles
INFO:     Started server process [37396]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

PS ...\frontend> python -m http.server 5500
Serving HTTP on :: port 5500 (http://[::]:5500/) ...

(venv) PS ...\backend> pytest tests/ -v
============================= test session starts ==============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 19 items

tests/test_cors.py::test_options_preflight_returns_cors_headers PASSED    [  5%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED [ 10%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED   [ 15%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED     [ 21%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED [ 26%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED   [ 31%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED [ 36%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED [ 42%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED [ 47%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED             [ 52%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED [ 57%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED [ 63%]
tests/test_tasks.py::test_patch_empty_json_body_returns_existing_task_unchanged PASSED [ 68%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED             [ 73%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED [ 78%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED [ 84%]
tests/test_tasks.py::test_patch_same_status_returns_200_and_keeps_status PASSED           [ 89%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED     [ 94%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED             [100%]
======================== 19 passed, 3 warnings in 0.40s ========================
```

## Backend test results

### Feature 1 tests

Command:
```
pytest tests/test_due_dates.py -v
```

Result: **13 passed, 1 warning in 0.34s**

All 13 tests:
- `test_create_task_with_valid_due_date_returns_201_and_due_date`
- `test_create_task_without_due_date_defaults_to_null`
- `test_create_task_with_invalid_due_date_returns_422`
- `test_patch_updates_due_date`
- `test_patch_due_date_null_clears_it`
- `test_patch_unrelated_field_preserves_due_date`
- `test_todo_task_with_past_due_date_is_overdue`
- `test_inprogress_task_with_past_due_date_is_overdue`
- `test_done_task_with_past_due_date_is_not_overdue`
- `test_task_without_due_date_is_not_overdue`
- `test_overdue_filter_returns_only_overdue_tasks`
- `test_overdue_filter_with_no_matches_returns_200_empty_list`
- `test_status_and_priority_filters_still_work_alongside_due_dates`

All 13 passed.

Warning: `StarletteDeprecationWarning` regarding `httpx`/`TestClient`. This is a warning only and did not cause a test failure.

### Full backend suite

Command:
```
pytest tests/ -v
```

Result: **32 passed, 2 warnings in 1.37s**

All existing tests and all Feature 1 tests passed, grouped by file:

**`test_cors.py`:**
- `test_options_preflight_returns_cors_headers`

**`test_due_dates.py`:**
- `test_create_task_with_valid_due_date_returns_201_and_due_date`
- `test_create_task_without_due_date_defaults_to_null`
- `test_create_task_with_invalid_due_date_returns_422`
- `test_patch_updates_due_date`
- `test_patch_due_date_null_clears_it`
- `test_patch_unrelated_field_preserves_due_date`
- `test_todo_task_with_past_due_date_is_overdue`
- `test_inprogress_task_with_past_due_date_is_overdue`
- `test_done_task_with_past_due_date_is_not_overdue`
- `test_task_without_due_date_is_not_overdue`
- `test_overdue_filter_returns_only_overdue_tasks`
- `test_overdue_filter_with_no_matches_returns_200_empty_list`
- `test_status_and_priority_filters_still_work_alongside_due_dates`

**`test_tasks.py`:**
- `test_create_task_valid_returns_201_with_full_body`
- `test_create_task_missing_title_returns_422`
- `test_create_task_blank_title_returns_422`
- `test_create_task_invalid_priority_returns_422`
- `test_create_task_unknown_field_returns_422`
- `test_list_tasks_empty_returns_200_and_empty_list`
- `test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list`
- `test_list_tasks_filter_by_priority_returns_only_matches`
- `test_get_task_by_id_returns_task`
- `test_get_task_by_id_not_found_returns_404_with_detail`
- `test_patch_partial_update_keeps_other_fields`
- `test_patch_empty_json_body_returns_existing_task_unchanged`
- `test_patch_not_found_returns_404`
- `test_patch_valid_transition_todo_to_inprogress_returns_200`
- `test_patch_invalid_transition_todo_to_done_returns_422`
- `test_patch_same_status_returns_200_and_keeps_status`
- `test_delete_existing_returns_204_no_body`
- `test_delete_missing_returns_404`

All 32 passed.

Warnings (not failures):
1. `StarletteDeprecationWarning` regarding `httpx`/`TestClient`.
2. `StarletteDeprecationWarning` that `HTTP_422_UNPROCESSABLE_ENTITY` is deprecated in favor of `HTTP_422_UNPROCESSABLE_CONTENT`.

### Status-transition verification

Command:
```
pytest tests/test_tasks.py -v -k "transition or same_status"
```

Result: **3 passed, 15 deselected, 2 warnings in 0.12s**

Verified behaviors:
- `ToDo -> InProgress` returns `200`.
- `ToDo -> Done` returns `422`.
- Same-status PATCH returns `200` and keeps the status unchanged.

Feature 1 did not alter the existing status-transition behavior.

## Manual browser checks

Feature 1 was manually verified in the browser.

1. **Due-date input**
   - Create/edit form contains a date-only due-date input.
   - A task can be created with a due date.
   - Due date can be edited.
   - Due date can be cleared.

2. **Due-date display**
   - Tasks with a due date display the due date on their cards.
   - Tasks without a due date do not display a due-date value.

3. **Overdue behavior**
   - Overdue status is taken from the backend `overdue` field.
   - Overdue tasks display a distinct Overdue badge.
   - Done tasks with past due dates are not treated as overdue.
   - Tasks without due dates are not treated as overdue.

4. **Overdue filter**
   - The "Overdue only" control is present.
   - Enabling it reloads the task list using `GET /tasks?overdue=true`.
   - Only backend-identified overdue tasks are shown.
   - Disabling it returns to the normal task list.

5. **Frontend source-of-truth constraint**
   - No JavaScript-side overdue date calculation was introduced.
   - The frontend renders the backend's `overdue` value.

## Behavior contract (before/after refactor)

**Before Feature 1:**
- Tasks supported title, description, status, priority, and assignee.
- `GET /tasks` supported `status` and `priority` filters.
- Status transitions were enforced by the backend.

**After Feature 1:**
- Existing behavior remains supported.
- Tasks additionally support an optional date-only `due_date`.
- PATCH can update or clear `due_date`.
- Backend exposes computed `overdue` status.
- `GET /tasks` supports `overdue=true`.
- Frontend displays due dates and backend-provided overdue status.
- Frontend provides an "Overdue only" filter.
- `overdue=false` remains out of scope.
- No JS-side overdue calculation was introduced.
- Existing status-transition behavior remains unchanged.

## Feature 2 manual browser checks

Feature 2 was manually verified in the browser. Developer-reported checklist, all passed:

- [x] Create task with tags
- [x] Tags trimmed/stored correctly
- [x] Tags appear as chips
- [x] No tags → no chips
- [x] Edit tags
- [x] Clear tags
- [x] Blank tag reaches backend → 422
- [x] Tag filter works
- [x] Tag filter is exact/case-sensitive
- [x] Clearing tag filter restores tasks
- [x] Tag filter + overdue filter work together
- [x] Existing status behavior intact
- [x] Existing priority behavior intact
- [x] Existing overdue behavior intact

**Result: PASSED**

## Break Test evidence

Two Feature 2 backend tests were deliberately broken (by mutating production code, not the test) and restored, to confirm each test actually catches the regression it claims to catch.

### Break 1 — `test_create_task_with_blank_tag_returns_422`

- **Mutation:** commented out the blank-tag rejection in `_validate_tags` (`backend/app/models.py`).
- **Result while broken:** test **FAILED** — `assert r.status_code == 422` got `201` instead of `422` (blank tag `"   "` was accepted).
- **Restore:** reinstated the `if not stripped: raise ValueError(...)` check.
- **Result after restore:** test **PASSED**.

### Break 2 — `test_tag_filter_is_case_sensitive`

- **Mutation:** changed the tag filter in `get_all_tasks` (`backend/app/storage.py`) to lowercase both sides before comparing (`tag.lower() in [t.lower() for t in task.tags]`).
- **Result while broken:** test **FAILED** — filtering `GET /tasks?tag=Bug` incorrectly matched a task tagged `"bug"`, returning 1 task instead of the expected empty list.
- **Restore:** reverted to the exact-match comparison (`tag in task.tags`).
- **Result after restore:** test **PASSED**.

### Post-restore confirmation

Full backend suite re-run after both restores: `pytest tests/ -v` → **47 passed, 2 warnings** (same pre-existing deprecation warnings as before, no new failures). No net changes remained in `models.py`/`storage.py` from the break/restore cycle.