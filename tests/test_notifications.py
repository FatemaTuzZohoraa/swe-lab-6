from unittest.mock import MagicMock, patch

import pytest

from app.events_bus import EventBus
from app.notifications import (ConsoleNotifier, EmailNotifier, NotifierFactory,
                               make_handler, mask_email)


def test_factory_creates_each_kind():
    assert isinstance(NotifierFactory.create("console"), ConsoleNotifier)
    assert isinstance(NotifierFactory.create("email"), EmailNotifier)


def test_factory_rejects_unknown_kind():
    with pytest.raises(ValueError):
        NotifierFactory.create("pigeon")


def test_mask_email_hides_name():
    assert mask_email("rahim@example.com") == "r***@example.com"


def test_console_notifier_records_message():
    n = ConsoleNotifier()
    n.send("a@test", "hi")
    assert n.sent == [("a@test", "hi")]


@patch("app.notifications.smtplib.SMTP")
def test_email_notifier_uses_mocked_smtp(smtp_cls):
    server = smtp_cls.return_value.__enter__.return_value
    EmailNotifier("smtp.test", 25, "lib@test").send("b@test", "hello")
    server.send_message.assert_called_once()


def test_observer_sends_notification_when_event_published():
    members, notifier, bus = MagicMock(), MagicMock(), EventBus()
    members.get.return_value = {"email": "x@test"}
    bus.subscribe("book_borrowed", make_handler(notifier, members))
    bus.publish("book_borrowed", {"member_id": 1, "message": "hi"})
    notifier.send.assert_called_once_with("x@test", "hi")
