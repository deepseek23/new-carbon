from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import ChallengeType, UserChallenge, ChallengeProgress
import json
@login_required
def index(request):
    """Display all available challenges"""
    # Get all active challenge types
    challenges = ChallengeType.objects.filter(is_active=True)
    
    # If user is authenticated, get their joined challenges
    user_challenges = []
    if request.user.is_authenticated:
        user_challenges = UserChallenge.objects.filter(
            user=request.user, 
            status='active'
        ).values_list('challenge_type_id', flat=True)
    
    context = {
        'challenges': challenges,
        'user_challenges': user_challenges,
    }
    return render(request, 'challenges/index.html', context)

@login_required
def join_challenge(request, challenge_id):
    """Allow user to join a challenge"""
    if request.method == 'POST':
        challenge_type = get_object_or_404(ChallengeType, id=challenge_id)
        
        # Check if user already joined this challenge
        existing_challenge = UserChallenge.objects.filter(
            user=request.user, 
            challenge_type=challenge_type
        ).first()
        
        if existing_challenge:
            if existing_challenge.status == 'active':
                return JsonResponse({
                    'success': False, 
                    'message': 'You have already joined this challenge!'
                })
            else:
                # Reactivate if previously completed/failed
                existing_challenge.status = 'active'
                existing_challenge.start_date = timezone.now()
                existing_challenge.progress_percentage = 0
                existing_challenge.save()
        else:
            # Create new user challenge
            UserChallenge.objects.create(
                user=request.user,
                challenge_type=challenge_type
            )
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully joined {challenge_type.title}!'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def my_challenges(request):
    """Display user's active challenges"""
    active_challenges = UserChallenge.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('challenge_type')
    
    # Get recent progress for each challenge
    challenges_with_progress = []
    for challenge in active_challenges:
        recent_progress = ChallengeProgress.objects.filter(
            user_challenge=challenge
        ).order_by('-date')[:7]  # Last 7 days
        
        challenges_with_progress.append({
            'challenge': challenge,
            'recent_progress': recent_progress,
            'completion_rate': calculate_completion_rate(challenge)
        })
    
    context = {
        'challenges_with_progress': challenges_with_progress,
    }
    return render(request, 'challenges/my_challenges.html', context)

@login_required
def update_progress(request, challenge_id):
    """Update daily progress for a challenge"""
    if request.method == 'POST':
        user_challenge = get_object_or_404(
            UserChallenge, 
            id=challenge_id, 
            user=request.user
        )
        
        data = json.loads(request.body)
        completed = data.get('completed', False)
        notes = data.get('notes', '')
        
        # Create or update today's progress
        progress, created = ChallengeProgress.objects.get_or_create(
            user_challenge=user_challenge,
            date=timezone.now().date(),
            defaults={
                'completed': completed,
                'notes': notes
            }
        )
        
        if not created:
            progress.completed = completed
            progress.notes = notes
            progress.save()
        
        # Update overall progress percentage
        update_challenge_progress(user_challenge)
        
        return JsonResponse({
            'success': True, 
            'message': 'Progress updated successfully!'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def calculate_completion_rate(user_challenge):
    """Calculate completion rate for a challenge"""
    if user_challenge.challenge_type.duration_days == 0:  # Ongoing challenge
        # For ongoing challenges, look at last 30 days
        total_days = 30
        start_date = timezone.now().date() - timezone.timedelta(days=30)
    else:
        # For timed challenges, calculate from start date
        total_days = user_challenge.challenge_type.duration_days
        start_date = user_challenge.start_date.date()
    
    completed_days = ChallengeProgress.objects.filter(
        user_challenge=user_challenge,
        completed=True,
        date__gte=start_date
    ).count()
    
    return min(100, int((completed_days / total_days) * 100)) if total_days > 0 else 0

def update_challenge_progress(user_challenge):
    """Update the overall progress percentage of a challenge"""
    completion_rate = calculate_completion_rate(user_challenge)
    user_challenge.progress_percentage = completion_rate
    
    # Mark as completed if reached 100% or time expired with good progress
    if completion_rate >= 100 or (user_challenge.is_expired and completion_rate >= 80):
        user_challenge.status = 'completed'
    elif user_challenge.is_expired and completion_rate < 50:
        user_challenge.status = 'failed'
    
    user_challenge.save()