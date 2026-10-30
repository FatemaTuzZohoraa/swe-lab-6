import sqlite3
from datetime import date

from flask import Blueprint, current_app, jsonify, render_template, request

from .services import ServiceError

bp = Blueprint("api", __name__)
TYPES = {"student", "teacher"}


def svc():
    return current_app.extensions["svc"]


@bp.errorhandler(ServiceError)
def handle_service_error(err):
    return jsonify(error=str(err)), err.status


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/members")
def add_member():
    """Register a library member
    ---
    tags: [Members]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [name, email]
          properties:
            name: {type: string}
            email: {type: string}
            member_type: {type: string, enum: [student, teacher]}
    responses:
      201: {description: Created}
      400: {description: Invalid input}
      409: {description: Email already exists}
    """
    d = request.get_json(silent=True) or {}
    name, email = d.get("name"), d.get("email")
    mtype = d.get("member_type", "student")
    if not name or not email or "@" not in email or mtype not in TYPES:
        return jsonify(error="Invalid input"), 400
    try:
        return jsonify(id=svc()["members"].add(name, email, mtype)), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Email already exists"), 409


@bp.get("/members")
def list_members():
    """List members (emails hidden for privacy)
    ---
    tags: [Members]
    responses:
      200: {description: List of members}
    """
    return jsonify(svc()["members"].list())


@bp.post("/books")
def add_book():
    """Add a book
    ---
    tags: [Books]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [title, author, copies]
          properties:
            title: {type: string}
            author: {type: string}
            copies: {type: integer}
    responses:
      201: {description: Created}
      400: {description: Invalid input}
    """
    d = request.get_json(silent=True) or {}
    try:
        title, author, copies = d["title"], d["author"], int(d["copies"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Invalid input"), 400
    if not title or not author or copies <= 0:
        return jsonify(error="Invalid input"), 400
    return jsonify(id=svc()["books"].add(title, author, copies)), 201


@bp.get("/books")
def list_books():
    """List books with available copies
    ---
    tags: [Books]
    responses:
      200: {description: List of books}
    """
    return jsonify(svc()["books"].list())


@bp.post("/loans")
def borrow():
    """Borrow a book (due in 14 days)
    ---
    tags: [Loans]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [member_id, book_id]
          properties:
            member_id: {type: integer}
            book_id: {type: integer}
    responses:
      201: {description: Borrowed}
      404: {description: Member or book not found}
      409: {description: No copies left or already borrowed}
    """
    d = request.get_json(silent=True) or {}
    if "member_id" not in d or "book_id" not in d:
        return jsonify(error="Invalid input"), 400
    return jsonify(id=svc()["loan"].borrow(d["member_id"], d["book_id"])), 201


@bp.get("/loans")
def list_active_loans():
    """List books currently borrowed
    ---
    tags: [Loans]
    responses:
      200: {description: Active loans}
    """
    return jsonify(svc()["loans"].list_active())


@bp.post("/loans/<int:loan_id>/return")
def return_book(loan_id):
    """Return a book (late fine is calculated)
    ---
    tags: [Loans]
    parameters:
      - in: path
        name: loan_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            returned_on: {type: string, description: "YYYY-MM-DD (optional, default today)"}
    responses:
      200: {description: Returned, fine in body}
      404: {description: Loan not found}
      409: {description: Already returned}
    """
    d = request.get_json(silent=True) or {}
    try:
        today = date.fromisoformat(d["returned_on"]) if d.get("returned_on") else None
    except ValueError:
        return jsonify(error="Invalid date"), 400
    return jsonify(fine=svc()["loan"].return_book(loan_id, today)), 200


@bp.get("/reports/summary")
def report():
    """Loans and fines summary
    ---
    tags: [Reports]
    responses:
      200: {description: Summary}
    """
    return jsonify(svc()["report"].summary())
