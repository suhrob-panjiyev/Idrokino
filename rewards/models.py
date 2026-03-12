from django.db import models
from academics.models import StudentProfile


class Reward(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, blank=True)
    needed_stars = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["needed_stars"]

    def __str__(self):
        return f"{self.title} ({self.needed_stars} stars)"


class StudentReward(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="student_rewards"
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name="student_rewards"
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "reward")
        ordering = ["-unlocked_at"]

    def __str__(self):
        return f"{self.student.user.username} - {self.reward.title}"