from typing import Dict, List, Optional
from datetime import datetime
from django.db.models import Sum
from django.contrib.auth.models import User
from core.models import Badge, UserBadge, StudyMaterial, StudyMilestone, UserProgress

class GamificationService:
    # XP rewards for different actions
    XP_REWARDS = {
        'complete_milestone': 50,
        'complete_quiz': 30,
        'read_material': 20,
        'bookmark_insight': 10
    }
    
    # Badge definitions with XP requirements
    BADGE_DEFINITIONS = [
        {
            'name': 'Study Starter',
            'description': 'Started your learning journey',
            'icon_url': '/static/badges/starter.svg',
            'xp_requirement': 100
        },
        {
            'name': 'Knowledge Seeker',
            'description': 'Completed 5 study milestones',
            'icon_url': '/static/badges/seeker.svg',
            'xp_requirement': 500
        },
        {
            'name': 'Quiz Master',
            'description': 'Achieved perfect scores in 3 quizzes',
            'icon_url': '/static/badges/master.svg',
            'xp_requirement': 1000
        },
        {
            'name': 'Dedicated Learner',
            'description': 'Studied for over 10 hours',
            'icon_url': '/static/badges/dedicated.svg',
            'xp_requirement': 2000
        },
        {
            'name': 'Subject Expert',
            'description': 'Mastered all materials in a subject',
            'icon_url': '/static/badges/expert.svg',
            'xp_requirement': 5000
        }
    ]
    
    @classmethod
    def initialize_badges(cls):
        """Create badge definitions if they don't exist."""
        for badge_def in cls.BADGE_DEFINITIONS:
            Badge.objects.get_or_create(
                name=badge_def['name'],
                defaults={
                    'description': badge_def['description'],
                    'icon_url': badge_def['icon_url'],
                    'xp_requirement': badge_def['xp_requirement']
                }
            )
    
    @classmethod
    def get_user_xp(cls, user: User) -> int:
        """Get total XP for a user."""
        total_xp = UserProgress.objects.filter(user=user).aggregate(Sum('xp_earned'))['xp_earned__sum']
        return total_xp or 0
    
    @classmethod
    def award_xp(cls, user: User, action_type: str) -> int:
        """Award XP for a specific action and return the amount awarded."""
        if action_type not in cls.XP_REWARDS:
            return 0
            
        xp_amount = cls.XP_REWARDS[action_type]
        return xp_amount
    
    @classmethod
    def check_and_award_badges(cls, user: User) -> List[Badge]:
        """Check if user qualifies for new badges and award them."""
        user_xp = cls.get_user_xp(user)
        new_badges = []
        
        # Get all badges user doesn't have yet
        earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        available_badges = Badge.objects.exclude(id__in=earned_badge_ids)
        
        for badge in available_badges:
            if user_xp >= badge.xp_requirement:
                UserBadge.objects.create(user=user, badge=badge)
                new_badges.append(badge)
        
        return new_badges
    
    @classmethod
    def get_progress_stats(cls, user: User) -> Dict:
        """Get comprehensive progress statistics for a user."""
        total_xp = cls.get_user_xp(user)
        completed_milestones = UserProgress.objects.filter(
            user=user,
            completed=True
        ).count()
        
        # Get next badge to achieve
        earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        next_badge = Badge.objects.exclude(id__in=earned_badge_ids)\
            .filter(xp_requirement__gt=total_xp)\
            .order_by('xp_requirement').first()
        
        return {
            'total_xp': total_xp,
            'completed_milestones': completed_milestones,
            'badges_earned': UserBadge.objects.filter(user=user).count(),
            'next_badge': {
                'name': next_badge.name if next_badge else None,
                'xp_required': next_badge.xp_requirement if next_badge else None,
                'xp_remaining': next_badge.xp_requirement - total_xp if next_badge else 0
            }
        }
    
    @classmethod
    def complete_milestone(cls, user: User, milestone: StudyMilestone) -> Dict:
        """Mark a milestone as completed and award XP."""
        # Check if already completed
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            study_material=milestone.study_material,
            milestone=milestone,
            defaults={'completed': True, 'completed_at': datetime.now()}
        )
        
        if created or not progress.completed:
            # Award XP for milestone completion
            xp_earned = cls.award_xp(user, 'complete_milestone') + milestone.xp_reward
            progress.xp_earned = xp_earned
            progress.completed = True
            progress.completed_at = datetime.now()
            progress.save()
            
            # Check for new badges
            new_badges = cls.check_and_award_badges(user)
            
            return {
                'xp_earned': xp_earned,
                'new_badges': [badge.name for badge in new_badges]
            }
        
        return {'xp_earned': 0, 'new_badges': []}