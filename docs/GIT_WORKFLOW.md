# Git / GitHub step-by-step (copy-paste in order)

Replace [YOUR_USERNAME]. First create an EMPTY GitHub repo named `library-app`.

## Step 1: initial commit and push
```bash
git init -b main
git add app run.py requirements.txt README.md .gitignore docs
git commit -m "chore: initial project skeleton with five modules"
git remote add origin https://github.com/[YOUR_USERNAME]/library-app.git
git push -u origin main
```

## Step 2: PR #1 (ACCEPTED): fine tests
```bash
git checkout -b feature/fine-tests
git add tests/__init__.py tests/test_fines.py
git commit -m "test(fines): cover Strategy classes and lookup"
git push -u origin feature/fine-tests
```
On GitHub: open PR, teammate (or your 2nd account) approves, merge. Then `git checkout main && git pull`.

## Step 3: PR #2 (REVISED): CI pipeline
```bash
git checkout -b feature/ci-pipeline
mkdir -p .github/workflows
# first, edit the LAST line of .github/workflows/ci.yml to just:   run: pytest
git add tests .github
git commit -m "ci: run pytest on every push and PR"
git push -u origin feature/ci-pipeline
```
Open PR. Reviewer comments: "Please enforce a coverage threshold." Then:
```bash
# restore last line to: run: pytest --cov=app --cov-report=term-missing --cov-fail-under=80
git commit -am "ci: enforce 80% coverage gate (review feedback)"
git push
```
Reviewer approves, merge. (GitHub blocks "request changes" on your own PR, so use a teammate or 2nd account.)

## Step 4: PR #3 (REJECTED): the alternative you rejected
```bash
git checkout main && git pull
git checkout -b experiment/fines-if-else
# in app/services.py replace get_strategy(...).fine(days_late) with an if/elif on member_type
git commit -am "experiment: replace Strategy with if/else chain"
git push -u origin experiment/fines-if-else
```
Open PR, comment "Rejected: every new fine rule would edit LoanService (violates Open/Closed)", then **Close pull request** without merging.

## Step 5: real TDD cycle (red, green)
```bash
git checkout main && git pull
git checkout -b feature/alumni-fine
```
RED: add to the END of `tests/test_fines.py`:
```python
from app.fines import AlumniFine

def test_alumni_fine_is_8_per_day():
    assert AlumniFine().fine(2) == 16
```
```bash
pytest          # FAILS with ImportError: this is RED
git add tests && git commit -m "test(fines): add failing test for AlumniFine (red)"
```
GREEN: add to `app/fines.py` (after TeacherFine):
```python
ALUMNI_RATE = 8

class AlumniFine(FineStrategy):
    def fine(self, days_late):
        return days_late * ALUMNI_RATE
```
```bash
pytest          # passes: GREEN
git add app && git commit -m "feat(fines): implement AlumniFine (green)"
git push -u origin feature/alumni-fine
```
Open PR, merge.

## Step 6: deliberate MERGE CONFLICT
Two branches change the same line: `STUDENT_RATE = 5` in `app/fines.py`.
```bash
git checkout main && git pull
git checkout -b feature/student-rate-6
sed -i 's/^STUDENT_RATE = [0-9]*/STUDENT_RATE = 6/' app/fines.py
git commit -am "feat(fines): raise student late fine to 6 BDT/day"
git push -u origin feature/student-rate-6

git checkout main
git checkout -b feature/student-rate-10
sed -i 's/^STUDENT_RATE = [0-9]*/STUDENT_RATE = 10/' app/fines.py
git commit -am "feat(fines): raise student late fine to 10 BDT/day"
git push -u origin feature/student-rate-10
```
(On macOS use `sed -i ''`, or just edit the line by hand.) Merge the "rate-6" PR on GitHub first, then:
```bash
git checkout feature/student-rate-10
git fetch origin && git merge origin/main
```
Git says `CONFLICT (content): Merge conflict in app/fines.py`. The file shows:
```
<<<<<<< HEAD
STUDENT_RATE = 10
=======
STUDENT_RATE = 6
>>>>>>> origin/main
```
Resolve: decide the real rule (keep the approved 6), delete the three marker lines, leave one line: `STUDENT_RATE = 6`
```bash
pytest                                  # passes: tests import the constant, not a fixed number
git add app/fines.py
git commit -m "merge: resolve STUDENT_RATE conflict, keep approved 6 BDT"
git push
```
Merge the PR. In your report, write what happened, how you decided, and add a screenshot of the markers.

## Step 7: finishing touches
- GitHub **Projects**: board (To do / Doing / Done), 5 issues (one per module), link PRs with "Closes #N".
- Release: `git tag -a v1.0.0 -m "First release" && git push origin v1.0.0`, then create a Release on GitHub.
- Report screenshots: `git log --oneline --graph --all`, PR list, green Actions run, conflict markers, `/apidocs/`.
