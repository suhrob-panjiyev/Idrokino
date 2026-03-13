from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from academics.models import StudentProfile, TeacherProfile, ParentProfile


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from academics.models import StudentProfile, TeacherProfile, ParentProfile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user.role == 'student':
                StudentProfile.objects.create(user=user)
            elif user.role == 'teacher':
                TeacherProfile.objects.create(user=user)
            elif user.role == 'parent':
                ParentProfile.objects.create(user=user)

            login(request, user)

            if user.role == "student":
                return redirect("student_dashboard")
            elif user.role == "teacher":
                return redirect("teacher_dashboard")
            elif user.role == "parent":
                return redirect("parent_dashboard")

            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == "student":
                return redirect("student_dashboard")
            elif user.role == "teacher":
                return redirect("teacher_dashboard")
            elif user.role == "parent":
                return redirect("parent_dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')