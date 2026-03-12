from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from academics.models import Subject, Assignment, Question, Choice, Submission
from .forms import (
    SubjectCreateForm,
    AssignmentCreateForm,
    QuestionCreateForm,
    ChoiceCreateForm,
)
from academics.models import StudentProfile, ClassGroup


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "teacher":
            return HttpResponseForbidden("Bu sahifa faqat o‘qituvchilar uchun.")

        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@teacher_required
def teacher_dashboard(request):
    user = request.user

    subjects = Subject.objects.filter(teacher=user).order_by("-id")
    assignments = Assignment.objects.filter(subject__teacher=user).order_by("-created_at")
    questions = Question.objects.filter(assignment__subject__teacher=user).order_by("-id")
    submissions = Submission.objects.filter(
        assignment__subject__teacher=user,
        is_completed=True
    ).order_by("-completed_at")

    recent_assignments = assignments[:5]
    recent_submissions = submissions[:5]

    context = {
        "subjects_count": subjects.count(),
        "assignments_count": assignments.count(),
        "questions_count": questions.count(),
        "submissions_count": submissions.count(),
        "recent_assignments": recent_assignments,
        "recent_submissions": recent_submissions,
    }

    return render(request, "teachers/dashboard.html", context)


@login_required
@teacher_required
def create_subject(request):
    if request.method == "POST":
        form = SubjectCreateForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = request.user
            subject.save()
            return redirect("teacher_dashboard")
    else:
        form = SubjectCreateForm(teacher=request.user)

    return render(request, "teachers/create_subject.html", {"form": form})


@login_required
@teacher_required
def create_assignment(request):
    if request.method == "POST":
        form = AssignmentCreateForm(request.POST, teacher=request.user)
        if form.is_valid():
            assignment = form.save()
            return redirect("add_question", assignment_id=assignment.id)
    else:
        form = AssignmentCreateForm(teacher=request.user)

    return render(request, "teachers/create_assignment.html", {"form": form})


@login_required
@teacher_required
def add_question(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        subject__teacher=request.user
    )

    questions = assignment.questions.all().order_by("order", "id")

    if request.method == "POST":
        form = QuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()
            return redirect("add_choices", question_id=question.id)
    else:
        form = QuestionCreateForm()

    context = {
        "assignment": assignment,
        "questions": questions,
        "form": form,
    }
    return render(request, "teachers/add_question.html", context)


@login_required
@teacher_required
def add_choices(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        assignment__subject__teacher=request.user
    )

    choices = question.choices.all().order_by("id")
    error_message = ""

    if request.method == "POST":
        form = ChoiceCreateForm(request.POST)
        if form.is_valid():
            new_choice = form.save(commit=False)

            if new_choice.is_correct and question.choices.filter(is_correct=True).exists():
                error_message = "Bu savolda allaqachon to‘g‘ri javob bor."
            else:
                new_choice.question = question
                new_choice.save()

                if "save_and_finish" in request.POST:
                    return redirect("teacher_dashboard")

                return redirect("add_choices", question_id=question.id)
    else:
        form = ChoiceCreateForm()

    context = {
        "question": question,
        "assignment": question.assignment,
        "choices": choices,
        "form": form,
        "error_message": error_message,
    }
    return render(request, "teachers/add_choices.html", context)


@login_required
@teacher_required
def teacher_assignments(request):
    assignments = Assignment.objects.filter(
        subject__teacher=request.user
    ).select_related("subject").order_by("-created_at")

    context = {
        "assignments": assignments,
    }
    return render(request, "teachers/assignments_list.html", context)


@login_required
@teacher_required
def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        subject__teacher=request.user
    )

    if request.method == "POST":
        form = AssignmentCreateForm(
            request.POST,
            instance=assignment,
            teacher=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Topshiriq muvaffaqiyatli yangilandi.")
            return redirect("teacher_assignments")
    else:
        form = AssignmentCreateForm(instance=assignment, teacher=request.user)

    context = {
        "assignment": assignment,
        "form": form,
    }
    return render(request, "teachers/assignment_edit.html", context)


@login_required
@teacher_required
def assignment_toggle_active(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        subject__teacher=request.user
    )

    if request.method == "POST":
        assignment.is_active = not assignment.is_active
        assignment.save(update_fields=["is_active"])

        if assignment.is_active:
            messages.success(request, "Topshiriq faol holatga o‘tkazildi.")
        else:
            messages.success(request, "Topshiriq nofaol holatga o‘tkazildi.")

    return redirect("teacher_assignments")


@login_required
@teacher_required
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        subject__teacher=request.user
    )

    submissions_exist = Submission.objects.filter(assignment=assignment).exists()

    if request.method == "POST":
        if submissions_exist:
            messages.error(
                request,
                "Bu topshiriq bo‘yicha natijalar mavjud. Uni o‘chirish o‘rniga nofaol qiling."
            )
            return redirect("teacher_assignments")

        assignment.delete()
        messages.success(request, "Topshiriq muvaffaqiyatli o‘chirildi.")
        return redirect("teacher_assignments")

    context = {
        "assignment": assignment,
        "submissions_exist": submissions_exist,
    }
    return render(request, "teachers/assignment_delete_confirm.html", context)


@login_required
@teacher_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related("subject"),
        id=assignment_id,
        subject__teacher=request.user
    )

    submissions = Submission.objects.filter(
        assignment=assignment,
        is_completed=True
    ).select_related("student__user").order_by("-completed_at")

    context = {
        "assignment": assignment,
        "submissions": submissions,
    }
    return render(request, "teachers/assignment_submissions.html", context)


@login_required
@teacher_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related(
            "student__user",
            "assignment",
            "assignment__subject",
        ).prefetch_related(
            "answers__question",
            "answers__selected_choice",
        ),
        id=submission_id,
        assignment__subject__teacher=request.user
    )

    answers = submission.answers.all().order_by("question__order", "id")
    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()

    context = {
        "submission": submission,
        "answers": answers,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
    }
    return render(request, "teachers/submission_detail.html", context)


@login_required
@teacher_required
def teacher_students(request):
    class_groups = ClassGroup.objects.filter(teacher=request.user).order_by("name")
    students = StudentProfile.objects.filter(
        class_group__teacher=request.user
    ).select_related("user", "class_group", "parent").order_by("class_group__name", "user__username")

    context = {
        "class_groups": class_groups,
        "students": students,
    }
    return render(request, "teachers/students_list.html", context)

@login_required
@teacher_required
def question_delete(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related("assignment__subject"),
        id=question_id,
        assignment__subject__teacher=request.user
    )

    assignment = question.assignment

    submissions_exist = Submission.objects.filter(
        assignment=assignment,
        answers__question=question
    ).exists()

    if request.method == "POST":
        if submissions_exist:
            messages.error(
                request,
                "Bu savol bo‘yicha natijalar mavjud. Uni o‘chirish mumkin emas."
            )
            return redirect("add_question", assignment_id=assignment.id)

        question.delete()
        messages.success(request, "Savol muvaffaqiyatli o‘chirildi.")
        return redirect("add_question", assignment_id=assignment.id)

    context = {
        "question": question,
        "assignment": assignment,
        "submissions_exist": submissions_exist,
    }

    return render(request, "teachers/question_delete_confirm.html", context)