# My Personal AI Usage Rules

## Rule 1 - What I will never paste
- Real `.env` contents, API keys, tokens, credentials, or any live secret — only `.env.example`-style placeholders.
- Real customer/user data, or anything regulated/PII — even if a project starts as a toy, I won't paste in real data "just to test."
- Unredacted local machine details — absolute paths with my real username, device hostname, or Git identity (I caught `C:\Users\BEY-DEV030\...` and `rawadsh` leaking into a review transcript this course; going forward I sanitize paths/usernames before they go into any tool or prompt library).
- Proprietary or employer code I'm not explicitly authorized to share — this course repo is mine to share; anything from work isn't, by default.
- Raw, unfiltered terminal session dumps — I'll trim to the relevant command/output, not paste the whole scrollback.

## Rule 2 - What I will always verify before accepting
- Any AI-claimed bug, fix, or finding gets independently reproduced before I trust it — not just re-read the code, actually run it (this course, I didn't accept the null-PATCH crash claims until I reproduced all three with TestClient/Node output in hand).
- Any file/line citation an AI gives me (a review, a summary, a report) gets checked against the real file before I repeat it as fact.
- Any severity or risk rating gets checked for whether it was quietly softened because "it's just a small/course project" — I explicitly reject that framing.
- Before an AI tool edits or touches a file, I get the exact proposed change shown to me first, and approve it — no silent multi-file edits.
- Anything an AI labels as "confirmed" but that I know it never actually opened/read gets relabeled "unverified" — I won't let confidence-sounding language stand in for evidence.

## Rule 3 - How I will record AI contributions
- Every substantive AI-assisted change goes in `prompt-log.md`: the actual prompt used, and whether I accepted, rejected, or edited the result.
- AI-generated findings (reviews, audits, risk tables) stay visually separate from my own manually-verified findings, with an explicit column showing what I personally confirmed vs. what the AI asserted.
- Any AI-generated risk or security classification gets a date stamped on it, since risk isn't static — e.g. a "Low" risk finding about my own code's unpatched bugs stops being "Low" the moment that code goes public.
- I keep track of which specific files an AI tool actually opened and read in a given session vs. which it's speaking about secondhand — if it didn't read `user-stories.md`, I don't let a summary imply that it did.

## When I will re-read this
30 days from today. Reminder set...
