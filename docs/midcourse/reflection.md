Overview

For this mid-course project I implemented two features on top of the existing task tracker:

Feature 1: Due dates and overdue filtering
Feature 2: Task tags and tag filtering

Both features were implemented incrementally using user stories, a mini-ADR, automated tests, manual browser verification, and break testing before being considered complete.

What went well

Working in small steps made the implementation much easier to manage.

Instead of writing everything at once, I first produced user stories, confirmed the requirements, created an implementation plan, implemented the backend, verified it with tests, then completed the frontend and manually verified the UI.

This reduced the chances of introducing regressions and made debugging much easier.

The automated test suite also grew alongside the implementation:

Baseline: 19 passing tests
After Feature 1: 32 passing tests
After Feature 2: 47 passing tests

Having dedicated tests for the new functionality gave confidence that later changes did not break earlier behaviour.

Challenges

The biggest challenge was avoiding assumptions that were not explicitly stated in the requirements.

Several implementation details needed to be confirmed before coding, including:

whether omitted tags should default to an empty list
the maximum number of tags
the maximum tag length
PATCH semantics for replacing tags
whether tag filtering should be case-sensitive

Confirming these decisions before implementation prevented unnecessary rework.

Another challenge was ensuring that validation happened only in the backend. For example, the frontend intentionally does not remove blank tag entries before sending them so that backend validation correctly returns HTTP 422.

AI assistance

AI was useful for:

drafting user stories
proposing implementation plans
generating repetitive test cases
suggesting backend and frontend code structure
helping organise the project documentation

However, I did not accept every AI suggestion without review.

Examples where I corrected or refined AI output include:

rewriting a user story whose wording did not match the intended requirement
correcting assumptions about Feature 2 before implementation
requiring the frontend to preserve blank tag entries so backend validation could be tested properly
deciding what information belonged in the verification documentation instead of accepting raw terminal output

This reinforced the importance of reviewing AI-generated content rather than treating it as automatically correct.

AI Tools and Their Impact

I used two AI tools during this project: ChatGPT and Claude Code.

ChatGPT was mainly used for planning, requirements clarification, reviewing implementation decisions, developing user stories and the mini-ADR, and helping structure the project documentation. I also used it to think through testing strategies and to review whether the implementation matched the approved requirements.
Claude Code was mainly used as the coding assistant. It inspected the existing project, edited the backend and frontend files, created automated tests, ran the test suite, and recorded the implementation and verification results in the project documentation.
One moment when AI helped

AI was particularly helpful when planning Feature 2. Claude Code identified several implementation decisions that were not completely explicit in the initial requirements, such as the maximum number and length of tags, whether PATCH should replace or append tags, and how tag filtering should behave. These questions were surfaced before implementation, allowing the requirements to be confirmed before code was written.

AI was also useful for generating the 15 focused tag tests and running the full regression suite, which made it easier to verify that the new functionality did not break existing behaviour.

One moment when AI slowed me down

AI sometimes spent extra time proposing or documenting assumptions that I already had a specific expectation for. This meant that I had to review the proposed stories and implementation plans carefully and correct or confirm individual details before allowing implementation to continue.

The structured approval process was useful, but it also added some extra back-and-forth compared with simply making the changes immediately.

One place where my review changed the result

The clearest example was the blank tag handling in Feature 2.

The frontend requirement was that comma-separated tags should be split and trimmed, but blank entries must not be filtered out before being sent to the backend. This was important because the backend must be responsible for rejecting blank tags with HTTP 422.

I specifically corrected the frontend implementation requirement so that an input such as bug,,urgent would send the blank entry to the backend rather than silently removing it. The browser verification later confirmed that a blank tag reached the backend and produced the expected 422 response.

This showed me that AI can implement requirements effectively, but human review is still necessary to catch assumptions and make sure the implementation matches the actual intended behaviour rather than just what seems reasonable to the AI.

Testing and verification

The project used several levels of verification:

automated backend unit tests
full regression testing after each feature
manual browser testing
break testing (mutation testing)

For the break tests I intentionally introduced two regressions:

removed blank-tag validation
made tag filtering case-insensitive

Both corresponding tests failed immediately, demonstrating that the tests genuinely detect those defects. After restoring the correct implementation, the full suite returned to 47 passing tests, providing confidence that the regressions had been fully removed.

Lessons learned

This project reinforced several software engineering practices:

clarify requirements before implementation
implement one feature at a time
write tests for new behaviour
rerun the full regression suite after changes
use break testing to verify that tests actually detect faults
treat AI as an assistant rather than an authority

Overall, the structured workflow made the project easier to manage and resulted in a documented implementation supported by automated tests, manual verification, and evidence that the tests are effective.