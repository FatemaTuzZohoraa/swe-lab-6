"""OBSERVER pattern (behavioral): publishers don't know who is listening."""
from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, name, handler):
        self._subs[name].append(handler)

    def publish(self, name, payload):
        for handler in list(self._subs[name]):
            handler(payload)
