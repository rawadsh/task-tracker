# Architecture — Context-Strategy Comparison Log

AI-Assisted Coding, Module 5 Prompt Library. This log compares three context
strategies used to generate the same architecture-document task
(`docs/architecture-A.md`, `docs/architecture-B.md`, `docs/architecture-C.md`)
and records which strategy was chosen for the canonical architecture
reference, and why.

- Strategy A — minimal context
- Strategy B — structured context (`AGENTS.md` + file summaries)
- Strategy C — targeted context (a small set of anchor files)

Findings below were checked against the actual source
(`backend/app/models.py`, `storage.py`, `business_rules.py`, `main.py`,
`AGENTS.md`, `frontend/index.html`) before being recorded here.

## 1. Strategy comparison table

| Strategy | Got right | Got wrong / missed / invented | Best suited for |
|---|---|---|---|
| **A — minimal context** | Data model, request flow, key files, and conventions all match source exactly, including frontend details (hardcoded `API_BASE = 'http://127.0.0.1:8000'`, CORS restricted to `:5500`) confirmed by reading `frontend/index.html` directly. Nothing invented. | No inline sourcing anywhere in the body — every claim reads with equal confidence whether it was checked or reconstructed. Uncertainty only surfaces in the closing "assumptions" section, so a reader can't tell mid-document which lines were verified. | A fast, single-narrative onboarding overview where one confident read of the system matters more than per-claim provenance. |
| **B — structured (AGENTS.md + file summaries)** | Same data model/flow/files/conventions correct, each tagged `[Source: ...]`. Uniquely caught that `business_rules.py`'s `VALID_TRANSITIONS` comment and docstring are **not** contradictory in the current file — meaning the README's `[VERIFY]` note flagging that contradiction is stale. | Explicitly did not open `frontend/index.html`, `tests/`, or `docs/midcourse/` — says so inline rather than asserting. Frontend behavior is sourced to AGENTS.md secondhand, not direct reading. No inventions; only gap is breadth. | Governance/audit-style docs — matches this repo's own Module 5 rule ("cite the actual files inspected," use "not confirmed") — where every claim needs a traceable source and stale-doc drift must be caught. |
| **C — targeted anchor files** | Most granular on what it actually read: correctly captured that `storage.add_task` normalizes `description` to `""` only when falsy, that `update_task` leaves `updated_at` untouched if no fields were set, and is the only draft to list `/health`/`/version` in "what the app does." | Read `main.py` (which contains the CORS middleware config) but still wrote "Frontend/backend interaction: not visible from the files I read" — undercounting evidence it had in hand. Never opened `business_rules.py`, so treats `is_overdue`/status-transition rules as an unread black box, unlike A and B. | Narrow, deep-dive questions about one or two specific modules (e.g. "how exactly does PATCH work") where precision on a small file set outweighs a full-system view. |

## 2. Verdict

For the final architecture doc, I chose **Strategy B**. This document is
itself a governance artifact — something future agents and reviewers will
treat as source of truth for the repo — so per-claim traceability matters
more than a single confident narrative (A) or depth on a narrow file set
(C). B is the only draft that caught real doc drift (the README's stale
claim about a contradiction in `business_rules.py` that no longer exists),
and its `[Source: ...]` tagging plus explicit "not confirmed" markers
mirror the citation discipline this repo's own Module 5 guardrails already
require. Its cost — three areas (frontend, tests, midcourse docs) left
explicitly unconfirmed — is honest incompleteness, not invented coverage.

## 3. Context-engineering rule

For a governance or audit-style doc that will be trusted as a standing
reference, I use Strategy B because inline per-claim sourcing lets me catch
stale claims elsewhere in the repo instead of silently repeating them. For
a quick one-off onboarding read where no one downstream needs to trace a
claim back to a file, I use Strategy A because a minimal-context pass
reconstructed the same architecture accurately without the overhead of
citation bookkeeping.