from django.contrib import admin
from .models import (
    ClassGroup,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    Subject,
    Assignment,
    Question,
    Choice,
    Submission,
    StudentAnswer,
    StudentProgress,
)

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "completed_assignments",
        "total_assignments",
        "progress_percent",
    )
    list_filter = ("subject",)
    search_fields = ("student__user__username", "subject__title")

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher")
    search_fields = ("name", "teacher__username")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "class_group", "parent", "total_points", "stars")
    list_filter = ("class_group",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "class_group")
    list_filter = ("class_group",)
    search_fields = ("title", "teacher__username")


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "assignment", "order")
    list_filter = ("assignment",)
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "points", "is_active", "created_at")
    list_filter = ("is_active", "subject")
    search_fields = ("title", "subject__title")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "score", "is_completed", "completed_at")
    list_filter = ("is_completed", "assignment")
    search_fields = ("student__user__username", "assignment__title")


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "question", "selected_choice", "is_correct")
    list_filter = ("is_correct",)