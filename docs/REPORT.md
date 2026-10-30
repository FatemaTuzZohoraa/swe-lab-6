# Project Report: Library Book Manager (CSE 3206)

## 1. Requirements
**Functional**
- FR1 Register members (student/teacher). FR2 Add books with number of copies.
- FR3 Borrow a book (due in 14 days; no copy left = rejected; same book twice = rejected).
- FR4 Return a book; late fine = late days x rate (rate depends on member type).
- FR5 Notify the member after borrow/return. FR6 Report total loans, active loans, total fines.

**Non-functional**
- NFR1 Data stored persistently (SQLite). NFR2 Extensible: a new fine rule or notifier = one new class.
- NFR3 Testable: >=80% coverage, DB/email mocked. NFR4 Security/privacy: no secrets in repo, masked emails in logs, input validation.
- NFR5 API documented with OpenAPI (Swagger).

**User stories**
- As a librarian, I want to add books so that members can borrow them.
- As a student, I want to borrow a book so that I can read it for 14 days.
- As a librarian, I want late fines calculated automatically so that I don't do it by hand.
- As a member, I want a confirmation message after borrowing.

**Prototype / mock-up:** [INSERT a paper sketch or Figma/Excalidraw screenshot of the book list page]

## 2. Process model: Agile (Scrum-lite)
Requirements were small and could change, so I built one module per short iteration and tracked work on a GitHub Projects board. Waterfall was rejected because it assumes frozen requirements and tests only at the end.

## 3. Design patterns
| Pattern (category) | Problem it solves | Rejected alternative |
|---|---|---|
| Strategy (behavioral) | Fine rules differ per member type and will grow | if/elif chain inside `return_book`: every new rule edits core code |
| Factory (creational) | Callers should not know how to build console/email notifiers | Creating `EmailNotifier(...)` everywhere: couples code to config, hard to test |
| Observer (behavioral) | Borrow/return must trigger messages without knowing who listens | Calling `notifier.send()` inside `LoanService`: tight coupling |

UML: `docs/UML.md`.

## 4. Testing
- TDD: test committed first and seen failing (red), then implementation (green); example: `AlumniFine`.
- Mocks: `MagicMock` for repositories and event bus; `patch("smtplib.SMTP")` for email: no real DB or network in unit tests.
- Selenium: UI test adds a book through the browser (runs in CI).
- Coverage: [PASTE `pytest --cov=app` output]. CI fails below 80%.

## 5. Configuration management
[Screenshots: branches, PR list (merged / revised / closed), merge conflict, `git log --graph`, green Actions run, Release.]

## 6. New tool: Swagger/OpenAPI (flasgger)
- Why: docs generated from code cannot drift away from the API.
- Alternative rejected: Postman collections (separate files that go stale).
- Real use: each endpoint's docstring is the spec; `/apidocs/` is a live page where endpoints can be tried; a test checks that it loads.
- [ADD your real struggle, e.g. YAML indentation in docstrings.]

## 7. AI usage declaration
[State tools used and what you did yourself.]
