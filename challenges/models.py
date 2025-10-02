from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ChallengeType(models.Model):
    """
    Predefined challenge types that users can join
    """
    DURATION_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('ongoing', 'Ongoing'),
    ]
    
    CATEGORY_CHOICES = [
        ('food', 'Food & Diet'),
        ('transport', 'Transportation'),
        ('waste', 'Waste Reduction'),
        ('energy', 'Energy Consumption'),
        ('shopping', 'Sustainable Shopping'),
        ('lifestyle', 'Lifestyle'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES)
    duration_days = models.IntegerField(help_text="Duration in days (0 for ongoing)")
    carbon_impact = models.DecimalField(max_digits=8, decimal_places=2, help_text="Estimated CO2 savings in kg")
    difficulty_level = models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    icon_color = models.CharField(max_length=20, default='green')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['category', 'difficulty_level']

class UserChallenge(models.Model):
    """
    Represents a user's participation in a specific challenge
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge_type = models.ForeignKey(ChallengeType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'challenge_type']  # User can only join each challenge once
    
    def __str__(self):
        return f'{self.user.username} - {self.challenge_type.title}'
    
    def save(self, *args, **kwargs):
        # Automatically set end_date based on challenge duration
        if not self.end_date and self.challenge_type.duration_days > 0:
            self.end_date = self.start_date + timedelta(days=self.challenge_type.duration_days)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.end_date:
            return timezone.now() > self.end_date
        return False
    
    @property
    def days_remaining(self):
        if self.end_date:
            remaining = self.end_date - timezone.now()
            return max(0, remaining.days)
        return None

class ChallengeProgress(models.Model):
    """
    Daily progress tracking for user challenges
    """
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, related_name='progress_entries')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    carbon_saved = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_challenge', 'date']  # One progress entry per day per challenge
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.user_challenge} - {self.date} - {"✓" if self.completed else "✗"}'
