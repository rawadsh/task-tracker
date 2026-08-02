# Mini-ADR — Due Dates + Overdue Filter, Tags/Labels

## 1. Context

The task tracker currently supports title, description, status, priority, and assignee on tasks, with status/priority filtering on `GET /tasks` and status-transition rules enforced server-side. Two features are being added for this mid-course assessment:

- **Due dates + overdue filter** — lets users flag deadlines and see which unfinished tasks have passed them, without adding scheduling/notification machinery.
- **Tags/labels** — lets users attach lightweight free-text labels to tasks and filter by them, without turning tags into a managed entity.

Both are additive extensions of the existing Task resource, chosen to stay inside the current in-memory, single-resource architecture.

## 2. Decision

**Due dates:**
- `due_date: Optional[date]` added to `TaskCreate`, `TaskUpdate`, `TaskResponse` in `models.py`. Pydantic's native `date` type handles `YYYY-MM-DD` parsing and produces `422` on malformed input with no custom validator needed.
- `due_date` lives inline on the same in-memory `Task` record in `storage.py` — no new storage structure.
- Overdue is **not stored**. It's a `@computed_field` property on `TaskResponse`, recalculated from `due_date`/`status` at serialization time (so a task that becomes overdue purely by the passage of time reflects that on the next read, without needing a write).
- The overdue rule itself (`is_overdue(due_date, status)`) lives in `business_rules.py`, alongside the existing status-transition rule, and is reused by both the computed field and the `GET /tasks?overdue=true` filter in `storage.py` — one source of truth.
- `main.py` gains an `overdue: bool | None` query param on `GET /tasks`, passed straight to storage.
- Frontend adds a date input to the task form and renders `due_date`/`overdue` exactly as the backend returns them — no client-side overdue math.

**Tags:**
- `tags: list[str]` added to `TaskCreate`, `TaskUpdate`, `TaskResponse` in `models.py`.
- Validation (trim whitespace, reject blank tags, bound max count and max length per tag) is a `field_validator` in `models.py` — the same pattern already used for `title` validation (`_validate_title`), since this is field-shape validation, not cross-field business logic.
- Tags are stored inline on the same in-memory `Task` record — no separate tag collection/entity.
- `storage.py`'s `get_all_tasks` gains a `tag` filter parameter alongside the existing `status`/`priority` filters.
- Frontend adds a tags input (comma-separated entry, rendered as chips) to the task form, chip display on cards, and a tag filter control.

## 3. Alternatives considered

- **Computing overdue in the frontend from `due_date`** — rejected: inconsistent across client clocks/timezones and violates the requirement that the backend be the sole source of truth.
- **Persisting `overdue` as a stored field, recomputed only on write** — rejected: would go stale between writes since overdue status can change with the passage of time alone, not just edits.
- **A separate `GET /tasks/overdue` endpoint** — rejected in favor of extending the existing `/tasks` endpoint with a query param, matching the existing `status`/`priority` filter style.
- **Tags as a separate resource/entity with its own model and endpoints** — rejected as over-engineered for an in-memory learning project; the approved scope explicitly treats tags as plain strings, not entities.
- **Tags as a single comma-separated string field** — considered (it was one of the two menu-listed options) but `list[str]` was chosen since it maps directly to JSON array semantics for chip rendering and filtering, avoiding duplicate split/join parsing logic on both ends.

## 4. Rejected as too complex or out of scope

- Due dates: due-*time* precision, timezone-aware due dates, recurring due dates, reminders/notifications, `overdue=false` filtering.
- Tags: tags as a managed entity/model with ownership, tag color customization, autocomplete/suggestion UI, case-insensitive tag deduplication beyond simple trimming.
- Both: authentication, a database, multi-tenancy, Docker/deployment infrastructure.

## 5. Consequences

**Benefits:** both features are additive field/query-param extensions of the existing Task model and existing filter pattern — no new architecture, no new storage layer, minimal surface area to test. Overdue as a computed field avoids a whole class of staleness bugs. Tag/due-date validation reuses the existing `models.py` field-validator convention, keeping the codebase consistent.

**Trade-offs:** in-memory storage means neither feature survives a restart (unchanged pre-existing limitation, not introduced by this work). The tag count/length bound is a simple guardrail, not a configurable or user-facing limit — acceptable for a small learning project but not production-grade. No tag normalization (e.g., case-folding) means `"Bug"` and `"bug"` are treated as distinct tags.

## 6. AI-assisted decision making

- **Feature 1:** an earlier AI-drafted plan proposed supporting `overdue=false` as a symmetric boolean filter alongside `overdue=true`. The human developer rejected this — only `overdue=true` is in scope; `overdue=false` is explicitly not implemented.
- No Tags-specific assumption has been corrected yet at this design stage — that section will only be added if/when it actually happens during implementation, not assumed in advance.

## 7. Implementation boundaries

**Included:**
- Due dates: optional `due_date` on create/update, null-clears-on-PATCH, `422` on invalid input, backend-computed `overdue`, `GET /tasks?overdue=true`, due date + overdue indicator in the UI.
- Tags: optional `tags` list on create/update, trim + blank-rejection + bounded count/length validation, tag chip display, tag filter in the UI.

**Not included:**
- `overdue=false` filtering, due-time/timezone handling, recurring dates, notifications.
- Tags as a standalone entity, tag colors/autocomplete, cross-tag deduplication logic, any auth/database/deployment changes.