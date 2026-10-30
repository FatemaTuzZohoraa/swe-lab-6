from datetime import date, timedelta

from .fines import get_strategy

LOAN_DAYS = 14


class ServiceError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class LoanService:
    def __init__(self, members, books, loans, bus):
        self.members, self.books, self.loans, self.bus = members, books, loans, bus

    def borrow(self, member_id, book_id, today=None):
        today = today or date.today()
        if not self.members.get(member_id):
            raise ServiceError("Member not found", 404)
        book = self.books.get(book_id)
        if not book:
            raise ServiceError("Book not found", 404)
        if self.loans.member_has_book(member_id, book_id):
            raise ServiceError("Member already has this book", 409)
        if self.loans.active_count(book_id) >= book["copies"]:
            raise ServiceError("No copies available", 409)
        due = today + timedelta(days=LOAN_DAYS)
        loan_id = self.loans.add(member_id, book_id, today.isoformat(), due.isoformat())
        self.bus.publish("book_borrowed", {
            "member_id": member_id,
            "message": f"You borrowed '{book['title']}'. Due on {due.isoformat()}."})
        return loan_id

    def return_book(self, loan_id, today=None):
        today = today or date.today()
        loan = self.loans.get(loan_id)
        if not loan:
            raise ServiceError("Loan not found", 404)
        if loan["returned_on"]:
            raise ServiceError("Book already returned", 409)
        member = self.members.get(loan["member_id"])
        days_late = max(0, (today - date.fromisoformat(loan["due_on"])).days)
        fine = get_strategy(member["member_type"]).fine(days_late)
        self.loans.mark_returned(loan_id, today.isoformat(), fine)
        self.bus.publish("book_returned", {
            "member_id": member["id"],
            "message": f"Book returned. Late fine: {fine} BDT."})
        return fine


class ReportService:
    def __init__(self, loans):
        self.loans = loans

    def summary(self):
        s = self.loans.summary()
        s["total_fines"] = round(s["total_fines"], 2)
        return s
