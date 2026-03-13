from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Email kiriting",
            "class": "form-input",
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Login kiriting",
                "class": "form-input",
            }),
            "role": forms.Select(attrs={
                "class": "form-input",
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user