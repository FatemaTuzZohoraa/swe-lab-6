from app.fines import (STUDENT_RATE, TEACHER_RATE, StudentFine, TeacherFine,
                       get_strategy)


def test_student_fine_is_rate_times_days():
    assert StudentFine().fine(3) == 3 * STUDENT_RATE


def test_teacher_fine_is_rate_times_days():
    assert TeacherFine().fine(3) == 3 * TEACHER_RATE


def test_no_late_days_means_no_fine():
    assert StudentFine().fine(0) == 0


def test_factory_picks_strategy_by_member_type():
    assert isinstance(get_strategy("teacher"), TeacherFine)
    assert isinstance(get_strategy("student"), StudentFine)
