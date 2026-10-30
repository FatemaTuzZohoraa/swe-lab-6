"""FACTORY pattern (creational): NotifierFactory builds the right notifier.
Secrets come from environment variables only."""
import logging
import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

log = logging.getLogger(__name__)


def mask_email(addr):
    """Privacy: never write a full email address to logs."""
    name, _, domain = addr.partition("@")
    return f"{name[:1]}***@{domain}"


class Notifier(ABC):
    @abstractmethod
    def send(self, to, message):
        ...


class ConsoleNotifier(Notifier):
    def __init__(self):
        self.sent = []

    def send(self, to, message):
        self.sent.append((to, message))
        log.info("notify %s: %s", mask_email(to), message)


class EmailNotifier(Notifier):
    def __init__(self, host, port, sender):
        self.host, self.port, self.sender = host, port, sender

    def send(self, to, message):
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = self.sender, to, "Library notice"
        msg.set_content(message)
        with smtplib.SMTP(self.host, self.port) as server:
            user = os.environ.get("SMTP_USER")  # [SMTP_USER_PLACEHOLDER]
            if user:
                server.starttls()
                server.login(user, os.environ["SMTP_PASSWORD"])  # [SMTP_PASSWORD_PLACEHOLDER]
            server.send_message(msg)


class NotifierFactory:
    @staticmethod
    def create(kind):
        if kind == "console":
            return ConsoleNotifier()
        if kind == "email":
            return EmailNotifier(
                os.environ.get("SMTP_HOST", "localhost"),
                int(os.environ.get("SMTP_PORT", "25")),
                os.environ.get("SMTP_SENDER", "library@[YOUR_DOMAIN]"))
        raise ValueError(f"Unknown notifier kind: {kind}")


def make_handler(notifier, members):
    """Observer callback: sends the message of any library event to the member."""
    def handle(payload):
        member = members.get(payload["member_id"])
        notifier.send(member["email"], payload["message"])
    return handle
