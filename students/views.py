from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from academics.models import (
    Assignment,
    StudentProfile,
    Submission,
    StudentAnswer,
    Choice,
    Subject,
    StudentProgress,
)
from rewards.models import Reward, StudentReward


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "student":
            return HttpResponseForbidden("Bu sahifa faqat o‘quvchilar uchun.")

        return view_func(request, *args, **kwargs)
    return wrapper


def unlock_student_rewards(student_profile):
    available_rewards = Reward.objects.filter(
        needed_stars__lte=student_profile.stars
    )

    new_rewards = []

    for reward in available_rewards:
        obj, created = StudentReward.objects.get_or_create(
            student=student_profile,
            reward=reward
        )
        if created:
            new_rewards.append(reward)

    return new_rewards

def update_student_progress(student_profile, subject):
    total_assignments = Assignment.objects.filter(
        subject=subject,
        is_active=True
    ).count()

    completed_assignments = Submission.objects.filter(
        student=student_profile,
        assignment__subject=subject,
        is_completed=True
    ).values("assignment_id").distinct().count()

    progress_percent = 0
    if total_assignments > 0:
        progress_percent = int((completed_assignments / total_assignments) * 100)

    StudentProgress.objects.update_or_create(
        student=student_profile,
        subject=subject,
        defaults={
            "completed_assignments": completed_assignments,
            "total_assignments": total_assignments,
            "progress_percent": progress_percent,
        }
    )

@login_required
@student_required
def student_dashboard(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    stars = student_profile.stars

    if stars >= 100:
        level_name = "Legend"
        level_icon = "👑"
    elif stars >= 50:
        level_name = "Master"
        level_icon = "🔥"
    elif stars >= 25:
        level_name = "Champion"
        level_icon = "🏆"
    elif stars >= 10:
        level_name = "Explorer"
        level_icon = "🚀"
    else:
        level_name = "Beginner"
        level_icon = "🌱"

    assignments = Assignment.objects.filter(
        is_active=True,
        subject__class_group=student_profile.class_group
    ).order_by("-created_at")

    completed_submission_ids = Submission.objects.filter(
        student=student_profile,
        is_completed=True
    ).values_list("assignment_id", flat=True)

    completed_assignment_ids = set(completed_submission_ids)

    dashboard_assignments = []
    for assignment in assignments[:5]:
        assignment.is_done = assignment.id in completed_assignment_ids
        dashboard_assignments.append(assignment)

    recent_submissions = Submission.objects.filter(
        student=student_profile,
        is_completed=True
    ).select_related("assignment").order_by("-completed_at")[:5]

    subject_progress_list = StudentProgress.objects.filter(
        student=student_profile
    ).select_related("subject").order_by("subject__title")

    unlocked_rewards_count = StudentReward.objects.filter(
        student=student_profile
    ).count()

    progress_percent = min(student_profile.total_points or 0, 100)

    context = {
        "student_profile": student_profile,
        "assignments": dashboard_assignments,
        "recent_submissions": recent_submissions,
        "total_points": student_profile.total_points,
        "total_stars": student_profile.stars,
        "assignments_count": assignments.count(),
        "rewards_count": unlocked_rewards_count,
        "progress_percent": progress_percent,
        "subject_progress_list": subject_progress_list,
        "level_name": level_name,
        "level_icon": level_icon,
    }

    return render(request, "students/dashboard.html", context)


@login_required
@student_required
def assignment_list(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    assignments = Assignment.objects.filter(
        is_active=True,
        subject__class_group=student_profile.class_group
    ).select_related("subject").order_by("-created_at")

    completed_submission_ids = Submission.objects.filter(
        student=student_profile,
        is_completed=True
    ).values_list("assignment_id", flat=True)

    completed_assignment_ids = set(completed_submission_ids)

    pending_assignments = []
    done_assignments = []

    for assignment in assignments:
        assignment.is_done = assignment.id in completed_assignment_ids
        if assignment.is_done:
            done_assignments.append(assignment)
        else:
            pending_assignments.append(assignment)

    context = {
        "pending_assignments": pending_assignments,
        "done_assignments": done_assignments,
    }
    return render(request, "students/assignments.html", context)


@login_required
@student_required
def assignment_detail(request, assignment_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        is_active=True,
        subject__class_group=student_profile.class_group
    )
    questions = assignment.questions.all().order_by("order", "id")

    existing_submission = Submission.objects.filter(
        student=student_profile,
        assignment=assignment,
        is_completed=True
    ).first()

    if existing_submission:
        return redirect("student_result", existing_submission.id)

    if request.method == "POST":
        submission = Submission.objects.create(
            student=student_profile,
            assignment=assignment,
            is_completed=True,
            completed_at=timezone.now(),
        )

        correct_count = 0

        for question in questions:
            selected_choice_id = request.POST.get(f"question_{question.id}")

            if selected_choice_id:
                selected_choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id,
                    question=question
                )
                is_correct = selected_choice.is_correct

                StudentAnswer.objects.create(
                    submission=submission,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

                if is_correct:
                    correct_count += 1

        score = correct_count * assignment.points
        earned_stars = score // 10

        submission.score = score
        submission.save()

        student_profile.total_points += score
        student_profile.stars += earned_stars
        student_profile.save()

        update_student_progress(student_profile, assignment.subject)

        new_rewards = unlock_student_rewards(student_profile)
        request.session["new_rewards"] = [r.title for r in new_rewards]

        return redirect("student_result", submission.id)

    return render(
        request,
        "students/assignment_detail.html",
        {
            "assignment": assignment,
            "questions": questions
        }
    )


@login_required
@student_required
def student_results(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    submissions = Submission.objects.filter(
        student=student_profile,
        is_completed=True
    ).select_related("assignment").order_by("-completed_at")

    return render(
        request,
        "students/results.html",
        {"submissions": submissions}
    )


@login_required
@student_required
def student_result(request, submission_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    submission = get_object_or_404(
        Submission.objects.select_related("assignment").prefetch_related(
            "answers__question",
            "answers__selected_choice",
        ),
        id=submission_id,
        student=student_profile
    )

    answers = submission.answers.all().order_by("question__order", "id")
    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()
    earned_stars = submission.score // 10
    percent = 0

    if total_questions > 0:
        percent = int((correct_answers / total_questions) * 100)

    # Session ichidan yangi rewardlarni olamiz va birdan o‘chirib yuboramiz
    new_rewards = request.session.pop("new_rewards", [])

    return render(
        request,
        "students/result.html",
        {
            "submission": submission,
            "earned_stars": earned_stars,
            "answers": answers,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "percent": percent,
            "new_rewards": new_rewards,
        }
    )


@login_required
@student_required
def stars_view(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    next_goal = 10
    if student_profile.stars >= 10:
        next_goal = 25
    if student_profile.stars >= 25:
        next_goal = 50
    if student_profile.stars >= 50:
        next_goal = 100
    if student_profile.stars >= 100:
        next_goal = student_profile.stars

    progress_percent = 100
    if next_goal > 0:
        previous_goal = 0
        if next_goal == 25:
            previous_goal = 10
        elif next_goal == 50:
            previous_goal = 25
        elif next_goal == 100:
            previous_goal = 50

        current_range = max(student_profile.stars - previous_goal, 0)
        total_range = max(next_goal - previous_goal, 1)
        progress_percent = min(int((current_range / total_range) * 100), 100)

    context = {
        "student_profile": student_profile,
        "next_goal": next_goal,
        "progress_percent": progress_percent,
    }
    return render(request, "students/stars.html", context)


@login_required
@student_required
def collection_view(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    rewards = Reward.objects.all().order_by("needed_stars")
    unlocked_reward_ids = set(
        StudentReward.objects.filter(student=student_profile)
        .values_list("reward_id", flat=True)
    )

    collection_items = []
    for reward in rewards:
        collection_items.append({
            "title": reward.title,
            "icon": reward.icon,
            "needed": reward.needed_stars,
            "description": reward.description,
            "unlocked": reward.id in unlocked_reward_ids,
        })

    return render(
        request,
        "students/collection.html",
        {
            "student_profile": student_profile,
            "rewards": collection_items,
        }
    )