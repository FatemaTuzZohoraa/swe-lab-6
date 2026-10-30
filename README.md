# Library Book Manager

**In one sentence:** a small web app where a library adds books, registers members, lends books for 14 days, and charges a late fine when a book is returned after its due date.

Built for CSE 3206 – Software Engineering Sessional (RUET). Flask + SQLite.

## The 5 modules
1. **Members**: register students and teachers
2. **Books**: add books and see available copies
3. **Loans**: borrow (14 days) and return books
4. **Fines**: late fee per day depends on member type (student 5 BDT, teacher 2 BDT)
5. **Reports + Notifications**: loan and fine summary, and a message after borrow/return

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py            # app:      http://127.0.0.1:5000
                         # API docs: http://127.0.0.1:5000/apidocs/   (Swagger / OpenAPI)
pytest --cov=app         # tests + coverage
```

## Design patterns
- **Strategy** (behavioral): `fines.py`
- **Factory** (creational): `notifications.py`
- **Observer** (behavioral): `events_bus.py`

## Security and privacy
- No secrets in the repo; SMTP credentials come from environment variables.
- Member emails are masked in logs; only name and email are stored.
- Future work: authentication (login) before real use.

## Git workflow
Branches: `feature/*`, `fix/*`, `docs/*`, `experiment/*`. Commit style: `feat:`, `test:`, `fix:`, `docs:`, `ci:`. Every change goes through a pull request.

## AI usage statement
[WRITE HONESTLY: which tool you used, for what, and that you can explain every part.]
