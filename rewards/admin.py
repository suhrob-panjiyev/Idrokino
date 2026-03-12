from django.contrib import admin
from .models import Reward, StudentReward


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "needed_stars")
    ordering = ("needed_stars",)


@admin.register(StudentReward)
class StudentRewardAdmin(admin.ModelAdmin):
    list_display = ("student", "reward", "unlocked_at")
    list_filter = ("reward", "unlocked_at")