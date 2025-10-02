from django.contrib import admin
from .models import ChallengeType, UserChallenge, ChallengeProgress

@admin.register(ChallengeType)
class ChallengeTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'duration_type', 'duration_days', 'difficulty_level', 'carbon_impact', 'is_active']
    list_filter = ['category', 'duration_type', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['category', 'difficulty_level']

@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge_type', 'status', 'progress_percentage', 'start_date', 'end_date']
    list_filter = ['status', 'challenge_type__category', 'start_date']
    search_fields = ['user__username', 'challenge_type__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChallengeProgress)
class ChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ['user_challenge', 'date', 'completed', 'carbon_saved']
    list_filter = ['completed', 'date', 'user_challenge__challenge_type__category']
    search_fields = ['user_challenge__user__username', 'user_challenge__challenge_type__title']
    date_hierarchy = 'date'
