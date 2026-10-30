from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from app.fines import STUDENT_RATE
from app.services import LoanService, ReportService, ServiceError


@pytest.fixture
def deps():
    members, books, loans, bus = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    members.get.return_value = {"id": 1, "member_type": "student", "email": "s@test"}
    books.get.return_value = {"id": 1, "title": "Python 101", "copies": 2}
    loans.member_has_book.return_value = False
    loans.active_count.return_value = 0
    loans.add.return_value = 7
    return members, books, loans, bus


def test_borrow_sets_due_date_and_notifies(deps):
    members, books, loans, bus = deps
    today = date(2026, 1, 1)
    assert LoanService(members, books, loans, bus).borrow(1, 1, today) == 7
    loans.add.assert_called_once_with(1, 1, "2026-01-01", "2026-01-15")
    bus.publish.assert_called_once()


def test_borrow_unknown_member(deps):
    members, books, loans, bus = deps
    members.get.return_value = None
    with pytest.raises(ServiceError) as e:
        LoanService(members, books, loans, bus).borrow(9, 1)
    assert e.value.status == 404


def test_borrow_unknown_book(deps):
    members, books, loans, bus = deps
    books.get.return_value = None
    with pytest.raises(ServiceError, match="Book not found"):
        LoanService(members, books, loans, bus).borrow(1, 9)


def test_borrow_when_no_copies_left(deps):
    members, books, loans, bus = deps
    loans.active_count.return_value = 2
    with pytest.raises(ServiceError, match="No copies"):
        LoanService(members, books, loans, bus).borrow(1, 1)
    loans.add.assert_not_called()


def test_borrow_same_book_twice(deps):
    members, books, loans, bus = deps
    loans.member_has_book.return_value = True
    with pytest.raises(ServiceError, match="already has"):
        LoanService(members, books, loans, bus).borrow(1, 1)


def test_return_late_calculates_fine(deps):
    members, books, loans, bus = deps
    loans.get.return_value = {"id": 7, "member_id": 1, "due_on": "2026-01-15", "returned_on": None}
    today = date(2026, 1, 15) + timedelta(days=3)
    fine = LoanService(members, books, loans, bus).return_book(7, today)
    assert fine == 3 * STUDENT_RATE
    loans.mark_returned.assert_called_once_with(7, today.isoformat(), fine)


def test_return_on_time_has_no_fine(deps):
    members, books, loans, bus = deps
    loans.get.return_value = {"id": 7, "member_id": 1, "due_on": "2026-01-15", "returned_on": None}
    assert LoanService(members, books, loans, bus).return_book(7, date(2026, 1, 10)) == 0


def test_return_twice_rejected(deps):
    members, books, loans, bus = deps
    loans.get.return_value = {"id": 7, "member_id": 1, "due_on": "2026-01-15", "returned_on": "2026-01-16"}
    with pytest.raises(ServiceError, match="already returned"):
        LoanService(members, books, loans, bus).return_book(7)


def test_return_unknown_loan(deps):
    members, books, loans, bus = deps
    loans.get.return_value = None
    with pytest.raises(ServiceError) as e:
        LoanService(members, books, loans, bus).return_book(99)
    assert e.value.status == 404


def test_report_rounds_fines():
    loans = MagicMock()
    loans.summary.return_value = {"total_loans": 2, "active_loans": 1, "total_fines": 10.0}
    assert ReportService(loans).summary()["total_fines"] == 10.0
