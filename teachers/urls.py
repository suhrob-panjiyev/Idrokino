from django.urls import path
from .views import (
    teacher_dashboard,
    create_subject,
    create_assignment,
    add_question,
    add_choices,
    teacher_assignments,
    assignment_edit,
    assignment_toggle_active,
    assignment_delete,
    assignment_submissions,
    submission_detail,
    teacher_students,
    question_delete,
)

urlpatterns = [
    path("dashboard/", teacher_dashboard, name="teacher_dashboard"),
    path("subjects/create/", create_subject, name="create_subject"),
    path("assignments/create/", create_assignment, name="create_assignment"),
    path("assignments/", teacher_assignments, name="teacher_assignments"),
    path("assignments/<int:assignment_id>/edit/", assignment_edit, name="assignment_edit"),
    path("assignments/<int:assignment_id>/toggle-active/", assignment_toggle_active, name="assignment_toggle_active"),
    path("assignments/<int:assignment_id>/delete/", assignment_delete, name="assignment_delete"),
    path("assignments/<int:assignment_id>/questions/add/", add_question, name="add_question"),
    path("assignments/<int:assignment_id>/submissions/", assignment_submissions, name="assignment_submissions"),
    path("questions/<int:question_id>/choices/add/", add_choices, name="add_choices"),
    path("submissions/<int:submission_id>/", submission_detail, name="submission_detail"),
    path("students/", teacher_students, name="teacher_students"),
    path("questions/<int:question_id>/delete/", question_delete, name="question_delete"),
]