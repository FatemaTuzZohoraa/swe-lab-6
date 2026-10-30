"""STRATEGY pattern (behavioral): each member type has its own late-fine rule."""
from abc import ABC, abstractmethod

STUDENT_RATE = 10
TEACHER_RATE = 2


class FineStrategy(ABC):
    @abstractmethod
    def fine(self, days_late):
        ...


class StudentFine(FineStrategy):
    def fine(self, days_late):
        return days_late * STUDENT_RATE


class TeacherFine(FineStrategy):
    def fine(self, days_late):
        return days_late * TEACHER_RATE


_STRATEGIES = {"student": StudentFine, "teacher": TeacherFine}


def get_strategy(member_type):
    return _STRATEGIES.get(member_type, StudentFine)()
