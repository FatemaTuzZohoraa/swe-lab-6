"""Repository layer: the only code that talks to the database.
Services use these classes, so tests can swap them for mocks."""
from .db import connect


class _Repo:
    def __init__(self, db_path):
        self.db_path = db_path

    def _one(self, sql, params=()):
        conn = connect(self.db_path)
        try:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def _all(self, sql, params=()):
        conn = connect(self.db_path)
        try:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()

    def _write(self, sql, params=()):
        conn = connect(self.db_path)
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


class MemberRepository(_Repo):
    def add(self, name, email, member_type):
        return self._write(
            "INSERT INTO members(name,email,member_type) VALUES(?,?,?)",
            (name, email, member_type))

    def get(self, member_id):
        return self._one("SELECT * FROM members WHERE id=?", (member_id,))


class BookRepository(_Repo):
    def add(self, title, author, copies):
        return self._write(
            "INSERT INTO books(title,author,copies) VALUES(?,?,?)",
            (title, author, copies))

    def get(self, book_id):
        return self._one("SELECT * FROM books WHERE id=?", (book_id,))

    def list(self):
        return self._all(
            "SELECT b.*, b.copies - (SELECT COUNT(*) FROM loans l "
            "WHERE l.book_id=b.id AND l.returned_on IS NULL) AS available "
            "FROM books b ORDER BY b.title")


class LoanRepository(_Repo):
    def add(self, member_id, book_id, borrowed_on, due_on):
        return self._write(
            "INSERT INTO loans(member_id,book_id,borrowed_on,due_on) VALUES(?,?,?,?)",
            (member_id, book_id, borrowed_on, due_on))

    def get(self, loan_id):
        return self._one("SELECT * FROM loans WHERE id=?", (loan_id,))

    def active_count(self, book_id):
        return self._one(
            "SELECT COUNT(*) AS c FROM loans WHERE book_id=? AND returned_on IS NULL",
            (book_id,))["c"]

    def member_has_book(self, member_id, book_id):
        return self._one(
            "SELECT 1 AS x FROM loans WHERE member_id=? AND book_id=? AND returned_on IS NULL",
            (member_id, book_id)) is not None

    def mark_returned(self, loan_id, returned_on, fine):
        self._write("UPDATE loans SET returned_on=?, fine=? WHERE id=?",
                    (returned_on, fine, loan_id))

    def summary(self):
        return self._one(
            "SELECT COUNT(*) AS total_loans, "
            "COALESCE(SUM(CASE WHEN returned_on IS NULL THEN 1 ELSE 0 END),0) AS active_loans, "
            "COALESCE(SUM(fine),0) AS total_fines FROM loans")
