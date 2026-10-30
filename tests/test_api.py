from datetime import date, timedelta

import pytest

from app import create_app
from app.fines import STUDENT_RATE


@pytest.fixture
def client(tmp_path):
    app = create_app({"DB_PATH": str(tmp_path / "t.db"), "TESTING": True})
    return app.test_client()


def _setup(client, copies=1):
    mid = client.post("/members", json={"name": "Rahim", "email": "r@test"}).get_json()["id"]
    bid = client.post("/books", json={"title": "Python 101", "author": "Ali",
                                      "copies": copies}).get_json()["id"]
    return mid, bid


def test_borrow_return_late_and_report(client):
    mid, bid = _setup(client)
    loan = client.post("/loans", json={"member_id": mid, "book_id": bid}).get_json()["id"]
    assert client.get("/books").get_json()[0]["available"] == 0
    late_day = (date.today() + timedelta(days=17)).isoformat()   # 3 days late
    r = client.post(f"/loans/{loan}/return", json={"returned_on": late_day})
    assert r.get_json()["fine"] == 3 * STUDENT_RATE
    assert client.get("/books").get_json()[0]["available"] == 1
    rep = client.get("/reports/summary").get_json()
    assert rep["total_loans"] == 1 and rep["active_loans"] == 0
    assert rep["total_fines"] == 3 * STUDENT_RATE


def test_no_copies_left(client):
    mid, bid = _setup(client)
    client.post("/loans", json={"member_id": mid, "book_id": bid})
    m2 = client.post("/members", json={"name": "B", "email": "b@test"}).get_json()["id"]
    assert client.post("/loans", json={"member_id": m2, "book_id": bid}).status_code == 409


def test_duplicate_email(client):
    client.post("/members", json={"name": "A", "email": "a@test"})
    assert client.post("/members", json={"name": "B", "email": "a@test"}).status_code == 409


def test_invalid_inputs(client):
    assert client.post("/members", json={"name": "A"}).status_code == 400
    assert client.post("/books", json={"title": "x"}).status_code == 400
    assert client.post("/loans", json={}).status_code == 400
    assert client.post("/loans/1/return", json={"returned_on": "bad"}).status_code == 400


def test_return_unknown_loan(client):
    assert client.post("/loans/99/return", json={}).status_code == 404


def test_swagger_page_available(client):
    assert client.get("/apidocs/").status_code == 200


def test_list_members_hides_email_and_lists_active_loans(client):
    mid, bid = _setup(client)
    members = client.get("/members").get_json()
    assert members[0]["name"] == "Rahim" and "email" not in members[0]
    loan = client.post("/loans", json={"member_id": mid, "book_id": bid}).get_json()["id"]
    active = client.get("/loans").get_json()
    assert active[0]["book"] == "Python 101" and active[0]["member"] == "Rahim"
    client.post(f"/loans/{loan}/return", json={})
    assert client.get("/loans").get_json() == []
