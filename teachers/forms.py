from django import forms
from academics.models import Subject, Assignment, Question, Choice, ClassGroup


class SubjectCreateForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["title", "class_group", "image"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Masalan: Matematika",
                "class": "form-input"
            }),
            "class_group": forms.Select(attrs={
                "class": "form-input"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher", None)
        super().__init__(*args, **kwargs)

        if teacher:
            self.fields["class_group"].queryset = ClassGroup.objects.filter(teacher=teacher)

        self.fields["title"].label = "Fan nomi"
        self.fields["class_group"].label = "Sinf"
        self.fields["image"].label = "Fan rasmi"


class AssignmentCreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["subject", "title", "description", "points", "is_active"]
        widgets = {
            "subject": forms.Select(attrs={
                "class": "form-input"
            }),
            "title": forms.TextInput(attrs={
                "placeholder": "Masalan: Qo‘shish amali",
                "class": "form-input"
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Topshiriq haqida qisqacha yozing",
                "class": "form-input"
            }),
            "points": forms.NumberInput(attrs={
                "min": 1,
                "class": "form-input"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-checkbox"
            }),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher", None)
        super().__init__(*args, **kwargs)

        if teacher:
            self.fields["subject"].queryset = Subject.objects.filter(teacher=teacher)

        self.fields["subject"].label = "Fan"
        self.fields["title"].label = "Topshiriq nomi"
        self.fields["description"].label = "Tavsif"
        self.fields["points"].label = "Ball"
        self.fields["is_active"].label = "Faol holatda bo‘lsin"


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "image", "order"]
        widgets = {
            "text": forms.TextInput(attrs={
                "placeholder": "Savol matnini kiriting",
                "class": "form-input"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-input"
            }),
            "order": forms.NumberInput(attrs={
                "min": 1,
                "class": "form-input"
            }),
        }


class ChoiceCreateForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "is_correct"]
        widgets = {
            "text": forms.TextInput(attrs={
                "placeholder": "Variant matni",
                "class": "form-input"
            }),
            "is_correct": forms.CheckboxInput(attrs={
                "class": "form-checkbox"
            }),
        }