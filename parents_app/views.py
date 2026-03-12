from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from academics.models import ParentProfile, StudentProfile, Submission, Assignment
from rewards.models import StudentReward


def parent_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "parent":
            return HttpResponseForbidden("Bu sahifa faqat ota-onalar uchun.")

        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@parent_required
def parent_dashboard(request):
    parent_profile = get_object_or_404(ParentProfile, user=request.user)

    child = StudentProfile.objects.select_related("user", "class_group").filter(
        parent=request.user
    ).first()

    recent_submissions = []
    recent_rewards = []
    child_points = 0
    child_stars = 0
    child_assignments = 0
    child_rewards_count = 0
    progress_percent = 0

    chart_labels = []
    chart_scores = []

    if child:
        completed_submissions = Submission.objects.filter(
            student=child,
            is_completed=True
        ).select_related("assignment")

        recent_submissions = completed_submissions.order_by("-completed_at")[:5]

        child_points = child.total_points
        child_stars = child.stars
        child_assignments = completed_submissions.count()

        child_rewards = StudentReward.objects.filter(
            student=child
        ).select_related("reward")

        child_rewards_count = child_rewards.count()
        recent_rewards = child_rewards.order_by("-unlocked_at")[:4]

        total_available_assignments = Assignment.objects.filter(
            is_active=True,
            subject__class_group=child.class_group
        ).count()

        if total_available_assignments > 0:
            progress_percent = int((child_assignments / total_available_assignments) * 100)
            if progress_percent > 100:
                progress_percent = 100

        chart_submissions = list(
            completed_submissions.order_by("completed_at")[:7]
        )

        chart_labels = [item.assignment.title for item in chart_submissions]
        chart_scores = [item.score for item in chart_submissions]

    context = {
        "parent_profile": parent_profile,
        "child": child,
        "child_points": child_points,
        "child_stars": child_stars,
        "child_assignments": child_assignments,
        "child_rewards_count": child_rewards_count,
        "recent_rewards": recent_rewards,
        "recent_submissions": recent_submissions,
        "chart_labels": chart_labels,
        "chart_scores": chart_scores,
        "progress_percent": progress_percent,
    }

    return render(request, "parents_app/dashboard.html", context)