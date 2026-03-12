from django.urls import path
from .views import parent_dashboard

urlpatterns = [
    path("", parent_dashboard, name="parent_dashboard"),
]