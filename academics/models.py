from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class ClassGroup(models.Model):
    name = models.CharField(max_length=50)  # masalan: 1-A

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='class_groups'
    )

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='student_profile'
    )

    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'parent'},
        related_name='children'
    )
    stars = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='teacher_profile'
    )

    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


class ParentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'parent'},
        related_name='parent_profile'
    )

    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username
    
class Subject(models.Model):

    title = models.CharField(max_length=100)

    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name="subjects"
    )

    image = models.ImageField(upload_to="subjects/", blank=True, null=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    points = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    text = models.CharField(max_length=500)

    image = models.ImageField(upload_to="questions/", blank=True, null=True)

    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )

    text = models.CharField(max_length=200)

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Submission(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"


class StudentAnswer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_in_answers'
    )

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.submission.student.user.username} - {self.question.text[:30]}"
    
class StudentProgress(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="progresses"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="student_progresses"
    )

    completed_assignments = models.IntegerField(default=0)
    total_assignments = models.IntegerField(default=0)
    progress_percent = models.IntegerField(default=0)

    class Meta:
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.title}"