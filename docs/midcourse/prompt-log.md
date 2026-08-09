# Prompt Log

## Weak Prompt → Stronger Prompt Example

### Weak Prompt — Initial workflow/setup prompt

**Original prompt given to Claude:**

> 1: i should have a document that contains .md files 2: create that / 3: start with it but take the current command runs in the terminal which are: [raw pasted terminal transcript]

**Why this was weak:**

The prompt was fragmented and relied on references to earlier steps instead of clearly stating the context, requirements, constraints, and approval boundaries. It also did not clearly distinguish between work I had already completed manually and work Claude was expected to perform.

**Rewritten stronger prompt:**

> You are a professional software developer for a Task Tracker project.
>
> **Context:**
> I am working through the project step-by-step and maintaining documentation under `docs/midcourse/`. I have already created and checked out the `mid-course-project` branch myself. I also have a real terminal transcript that I want to use as verification evidence.
>
> **Requirements:**
> - Create the `docs/midcourse/` directory if it does not already exist.
> - Create/update `verification.md` using the exact terminal transcript I provide as the baseline verification evidence.
> - Create/update `prompt-log.md` and record that I rejected having the AI perform the branch-creation step and that I manually edited the later steps.
> - Use my actual terminal output rather than inventing example command results.
> - Stop and let me review the documentation before making further implementation changes.
>
> **Not to do:**
> - Do not create or switch branches; I already handled that manually.
> - Do not invent test results, terminal output, or verification evidence.
> - Do not modify application code.
> - Do not proceed to implementation until I approve the documentation.
>
> **Expected result:**
> Create the documentation scaffolding and accurately record the actual workflow/history, then stop for review.

**What Claude returned:**

Claude created the documentation scaffolding and used the supplied terminal transcript as the baseline evidence. The workflow history was also recorded, including that I had rejected having Claude perform the branch-creation step and had manually edited later steps.

**What I accepted/edited/rejected:**

I accepted the overall documentation workflow.

I had already rejected the AI performing the branch-creation step, so that remained a manually completed action.

I later edited the verification documentation to remove unnecessary WatchFiles reload noise and restructure the verification evidence into clearer sections rather than leaving it as a raw terminal transcript.

**Why the stronger prompt was better:**

The rewritten version made the context, exact responsibilities, constraints, and approval gate explicit. This reduced ambiguity and made it clearer which work belonged to me and which work belonged to Claude.


## Feature 1 — Due Dates + Overdue Filter

### Prompt 1 — Feature 1 user stories

**Prompt given to Claude:**

> You are a professional software developer working on a Task Tracker project.
>
> **Context:**
> The project is implementing Feature 1 — Due Dates + Overdue Filter. The feature needs to fit the existing Task Tracker backend, frontend, and status-transition behavior. The project uses an AI-assisted development workflow where requirements and assumptions are reviewed before implementation.
>
> **Requirements:**
> - Propose user stories for Feature 1.
> - Cover optional task due dates.
> - Due dates must be date-only.
> - Cover how overdue tasks are determined.
> - Overdue status must be owned by the backend.
> - Cover an overdue filter.
> - Cover the frontend display/behavior required for the feature.
> - Each story must include an ID, user story, 2–3 acceptance criteria, and notes/assumptions.
> - Identify assumptions that a human reviewer should confirm or correct.
> - Stop for approval before creating or modifying implementation files.
>
> **Not to do:**
> - Do not implement the feature yet.
> - Do not modify backend or frontend files.
> - Do not change existing status-transition behavior.
> - Do not assume requirements that were not specified.
> - Do not treat `overdue=false` as automatically required.

**What Claude returned:**

Claude proposed five Feature 1 stories covering:
- creating tasks with due dates
- updating and clearing due dates
- determining overdue status
- filtering overdue tasks
- displaying due dates/overdue status in the frontend

Claude also identified assumptions around PATCH clearing behavior and `overdue=false`.

**What I accepted/edited/rejected:**

I accepted the overall story structure and acceptance criteria.

I rejected the wording that described overdue tasks as tasks needing **"urgent attention"**, because that benefit had not been requested.

I changed the story so that the benefit focused on distinguishing genuinely overdue tasks from completed tasks whose due dates had passed.

I also confirmed that `overdue=false` was out of scope.

---

### Prompt 2 — Feature 1 implementation


Weak Prompt → Strong Prompt — Feature 1
Original weak prompt

Prompt given to Claude:

Add due dates and an overdue filter to my Task Tracker application.

Tasks should be able to have due dates and users should be able to filter overdue tasks.

Also update the frontend to show the due date and overdue information.

What Claude returned/did:

Claude first loaded the project-specific workflow instructions and reviewed the existing Feature 1 documentation and implementation files. It also checked the current git branch and attempted to run the backend tests.

The initial test attempt failed because pytest was not available through the Python interpreter Claude first used. Claude then located the project's existing virtual environment and its pytest executable.

What I accepted/edited/rejected:

The implementation request itself was subsequently developed through the project's approved Feature 1 planning process. The final Feature 1 implementation added due dates, backend-owned overdue status, overdue filtering, and the corresponding frontend display/filter behavior while preserving existing status-transition behavior.

The resulting planning work covered:

    optional due dates
    date-only due dates
    backend-owned overdue calculation
    ToDo/InProgress past-due tasks being overdue
    Done tasks not being overdue
    tasks without due dates not being overdue
    overdue filtering
    frontend due-date/overdue behavior
    preserving existing status-transition behavior

Why it was weak:
    It combined planning and implementation into one instruction.
    It did not define the exact acceptance criteria.
    It did not explain how Done tasks should behave when their due date has passed.
    It did not specify the PATCH behavior for clearing a due date.
    It did not define where overdue logic should live.
    It did not establish an approval gate before implementation.
    It did not explicitly exclude overdue=false.


** Rewritten strong prompt given to Claude:**

> You are a professional software developer working on a Task Tracker project.
>
> **Context:**
> Feature 1 — Due Dates + Overdue Filter has been approved. The existing Task Tracker already has task CRUD behavior and status-transition rules. Feature 1 must add due-date and overdue functionality without changing the existing status-transition behavior.
>
> **Requirements:**
> - Add an optional `due_date`.
> - `due_date` must be date-only.
> - Invalid due-date input must return `422`.
> - PATCH with `due_date: null` must clear the due date.
> - Overdue must be calculated by the backend.
> - ToDo tasks with a past due date are overdue.
> - InProgress tasks with a past due date are overdue.
> - Done tasks are never overdue.
> - Tasks without a due date are never overdue.
> - Support `GET /tasks?overdue=true`.
> - Add the required frontend due-date input and display.
> - Display the backend-provided overdue state.
> - Add the overdue filter to the frontend.
> - Add focused tests for the feature.
>
> **Not to do:**
> - Do not implement `overdue=false`.
> - Do not calculate overdue in JavaScript.
> - Do not change `VALID_TRANSITIONS`.
> - Do not change existing status-transition behavior.
> - Do not modify unrelated functionality.
> - Do not add features that are outside the approved Feature 1 scope.

**What Claude returned:**

Claude implemented the due-date model fields, backend overdue calculation, overdue filtering, frontend due-date display/filtering, and focused Feature 1 tests.

**What I accepted/edited/rejected:**

I accepted the implementation because it followed the approved scope.

The existing status-transition rules were left unchanged.

---

### Prompt 3 — Feature 1 verification

**Prompt given to Claude:**

> You are a professional software developer working on a Task Tracker project.
>
> **Context:**
> Feature 1 — Due Dates + Overdue Filter has been implemented. The purpose of this step is verification, not additional implementation.
>
> **Requirements:**
> - Run the Feature 1 focused tests.
> - Run the full backend test suite.
> - Run the status-transition-focused tests.
> - Report the exact results.
> - Confirm that the existing status-transition behavior remains intact.
> - Verify the frontend behavior manually.
>
> **Not to do:**
> - Do not modify implementation files just to make tests pass.
> - Do not change status-transition rules.
> - Do not invent test results.
> - Do not add unrelated fixes.

**What Claude returned:**

Claude reported:
- Feature 1 tests: **13 passed**
- Full backend suite: **32 passed**
- Status-transition tests: **3 passed**
- Manual frontend verification: passed

**What I accepted/edited/rejected:**

I accepted the verification results.

The status-transition behavior remained intact, including valid transitions, invalid transitions, and same-status updates.

---

# Feature 2 — Tags/Labels

### Prompt 1 — Feature 2 user stories

**Prompt given to Claude:**

> You are a professional software developer working on a Task Tracker project.
>
> **Context:**
> Feature 2 is Tags/Labels. The approved direction is to keep tags simple and store them inline on the Task as a list of strings. The feature needs backend validation, tag filtering, and frontend tag input/chip/filter behavior.
>
> **Requirements:**
> - Propose the Feature 2 user stories.
> - Cover creating tasks with tags.
> - Tags must be trimmed.
> - Blank tags must be rejected.
> - Cover maximum tag count and maximum tag length.
> - Cover PATCH tag behavior.
> - Cover `GET /tasks?tag=...` filtering.
> - Cover frontend tag input.
> - Cover tag chips.
> - Cover frontend tag filtering.
> - Use the approved mini-ADR as the source of truth.
> - Identify assumptions that require human confirmation.
> - Stop before implementation and wait for approval.
>
> **Not to do:**
> - Do not create a separate tag entity/model.
> - Do not add tag colors.
> - Do not add autocomplete or suggestions.
> - Do not add case-insensitive deduplication.
> - Do not implement the feature yet.
> - Do not modify implementation files before approval.

**What Claude returned:**

Claude proposed five stories and identified these assumptions:
- omitted tags should default to `[]`
- maximum 10 tags
- maximum 30 characters per tag
- PATCH should replace the full tag list
- tag filtering should be single-value, exact-match, and case-sensitive

**What I accepted/edited/rejected:**

I confirmed all five assumptions.

None of those technical assumptions needed changing. I required them to be treated as confirmed decisions rather than remaining open assumptions.

---

### Prompt 2 — Feature 2 backend implementation


Weak Prompt → Strong Prompt — Feature 2
Original weak prompt

Add tags to the Task Tracker application. Users should be able to add tags to tasks, edit them, and filter tasks by tag. Add the required backend. Keep the tags simple

AI response:

Claude explained that the prompt was too broad and that it would likely make several implementation decisions implicitly instead of stopping for clarification.

It specifically identified these likely assumptions:

Tag data structure: Claude would probably choose list[str] on the Task model because the prompt said to keep tags simple.
Trimming: It might trim tags, but the weak prompt did not actually require trimming.

Blank tags: Claude might silently remove empty entries instead of rejecting them with 422. It explicitly recognized that this would be wrong for the actual project requirement, where blank tags must reach the backend and be rejected.
Maximum count/length: The weak prompt did not specify limits, so Claude might invent limits or omit them. The approved project requirements later established 10 tags maximum and 30 characters maximum per tag.

PATCH behavior: The prompt did not say whether PATCH should append/merge tags or completely replace them. Claude identified this as an important ambiguity.

Filtering: The prompt did not specify whether tag filtering should be:
single-tag or multi-tag,
exact or partial,
case-sensitive or case-insensitive.

Workflow: Claude would likely implement backend, frontend, and tests in one pass instead of stopping for the project's required approval checkpoint.

Important observation from Claude: the weak prompt could produce a technically working feature while still violating the project's actual requirements, because the missing decisions would be silently invented during implementation.

The resulting planning work covered:

    tags stored as list[str]
    trimming tags
    rejecting blank tags
    maximum 10 tags
    maximum 30 characters per tag
    omitted tags defaulting to []
    PATCH using full-replacement semantics
    tags: [] clearing tags
    omitted PATCH tags preserving existing tags
    single-value exact, case-sensitive tag filtering
    frontend tag input, chips, and filtering

Why it was weak:
    It did not define the tag data structure.
    It did not specify trimming or blank-tag behavior.
    It did not define the maximum number or length of tags.
    It did not define PATCH semantics.
    It did not specify whether filtering was case-sensitive.
    It did not specify whether filtering supported one or multiple tags.
    It did not define the frontend blank-entry behavior.
    It did not establish the backend/frontend implementation boundary.
    It did not explicitly exclude tag entities, colors, autocomplete, etc.

** Rewritten strong prompt given to Claude:**

> You are a professional software developer working on a Task Tracker project.
>
> **Context:**
> Feature 2 backend implementation has been approved. The backend must support tags as simple strings stored inline on tasks. The frontend will be implemented separately after the backend is verified.
>
> **Requirements:**
> - Implement only the backend portion of Feature 2.
> - Modify:
>   - `backend/app/models.py`
>   - `backend/app/storage.py`
>   - `backend/app/main.py`
> - Create:
>   - `backend/tests/test_tags.py`
> - Tags are a list of strings.
> - Trim tag values.
> - Reject blank tags with `422`.
> - Maximum 10 tags per task.
> - Maximum 30 characters per tag.
> - Omitted tags default to `[]`.
> - PATCH `tags` uses full-replacement semantics.
> - PATCH `tags: []` clears the tag list.
> - Omitted `tags` on PATCH preserves the existing tag list.
> - `GET /tasks?tag=...` performs exact, case-sensitive matching.
> - Add focused tests covering these behaviors.
> - Run the Feature 2 tests.
> - Run the full backend suite.
> - Report the exact results before stopping.
>
> **Important frontend correction for the later frontend step:**
> The comma-separated tag input must split and trim entries but must NOT filter out blank entries before sending. Blank entries must reach the backend so the backend's `422` validation actually fires from real UI input.
>
> **Not to do:**
> - Do not modify `business_rules.py`.
> - Do not modify `frontend/index.html` during this step.
> - Do not add a separate tag entity/model.
> - Do not add tag colors.
> - Do not add autocomplete.
> - Do not add unrelated backend functionality.
> - Do not duplicate validation in unrelated layers.

**What Claude returned:**

Claude implemented:
- `MAX_TAG_COUNT`
- `MAX_TAG_LENGTH`
- `_validate_tags`
- tag fields on create/update/response models
- tag storage
- exact/case-sensitive tag filtering
- the `tag` query parameter
- 15 Feature 2 tests

Test results:

```text
pytest tests/test_tags.py -v
15 passed