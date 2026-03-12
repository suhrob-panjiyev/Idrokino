from django.urls import path
from .views import (
    student_dashboard,
    assignment_list,
    assignment_detail,
    student_results,
    student_result,
    stars_view,
    collection_view,
)

urlpatterns = [
    path("dashboard/", student_dashboard, name="student_dashboard"),
    path("assignments/", assignment_list, name="student_assignments"),
    path("assignment/<int:assignment_id>/", assignment_detail, name="assignment_detail"),
    path("results/", student_results, name="student_results"),
    path("result/<int:submission_id>/", student_result, name="student_result"),
    path("stars/", stars_view, name="student_stars"),
    path("collection/", collection_view, name="collection"),
]