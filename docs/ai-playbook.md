# AI Coding Playbook

## 1. When I reach for AI first
- Drafting user stories, implementation plans, and doc structure before any code is written
- Generating repetitive/boilerplate test cases once requirements are already confirmed
- Surfacing implementation questions not explicit in the requirements (edge cases, bounds, PATCH semantics) before coding starts

## 2. When I do not reach for AI
- Deciding what's actually in/out of scope for a feature — that's my call to confirm, not delegate (mini-ADR decisions)
- Judging whether a risk/severity rating is really "Low" just because it's a small/course project — I reject that framing myself
- Final call on whether an AI-claimed bug or fix is real — I don't accept it until I've reproduced it myself

## 3. My non-negotiables
- No authentication added, no database introduced, no public response shape changed without my explicit approval
- Before any file/code/config change, I get the exact diff shown to me and approve it first — no silent multi-file edits
- Never paste real secrets/credentials, real customer/PII data, unredacted local paths/usernames/Git identity, or unauthorized proprietary/employer code into any AI tool

## 4. My review rules
- Any AI-claimed bug or fix gets independently reproduced (TestClient/browser/Node output in hand), not just re-read
- Every file/line citation an AI gives me gets checked against the real file before I repeat it as fact
- AI-generated findings stay visually separate from my own manually-verified findings, with an explicit column showing what I personally confirmed vs. what the AI asserted

## 5. What I am still figuring out
- Where to draw the line between "show me every diff" and moving faster on genuinely low-stakes changes — the full approval loop added back-and-forth I noticed but haven't resolved
- How to scale the AI-findings-vs-manual-findings reconciliation process beyond a single course project
- Whether my `docs/ai-usage.md` rules need to change now that the 30-day re-read is due

---

## Decision Card

**AI-Assisted Coding - Module 5 Prompt Library**
- For a new feature I reach for: user stories + an implementation plan, confirmed before any code is written
- For a code review I reach for: a dual-track pass — AI findings and my own manual findings — then reconciled side by side
- For debugging I reach for: independent reproduction (TestClient/browser/Node) before trusting any AI-claimed root cause
- For infrastructure I reach for: the same reproduce-and-verify discipline extended to CI/Dockerfile/dependency config, not just app code
- I will never paste real secrets/credentials, real customer/PII data, unredacted local paths/usernames/Git identity, or unauthorized proprietary/employer code into an AI tool.
- My one rule is: get the exact proposed change shown to me first, and approve it — no silent multi-file edits.