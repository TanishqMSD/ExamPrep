from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class ScrapedContent(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=200)
    raw_content = models.TextField()
    source_type = models.CharField(max_length=50, choices=[
        ('webpage', 'Web Page'),
        ('pdf', 'PDF Document')
    ])
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.title)

class StudyMaterial(models.Model):
    scraped_content = models.ForeignKey(ScrapedContent, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    eli5_explanation = models.TextField(help_text="Explain Like I'm 5 version")
    study_duration = models.IntegerField(help_text="Estimated study duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.title)

class KeyConcept(models.Model):
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='key_concepts')
    concept = models.CharField(max_length=200)
    definition = models.TextField()

    def __str__(self) -> str:
        return str(self.concept)

class StudyMilestone(models.Model):
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField()
    xp_reward = models.IntegerField(null=False, default=models.NOT_PROVIDED)

    class Meta:
        ordering = ['order']

    def __str__(self) ->str:
        return str(self.title)

class BookmarkedInsight(models.Model):
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)
    content = models.TextField()
    importance_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content)[:50] + "..."

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)
    milestone = models.ForeignKey(StudyMilestone, on_delete=models.CASCADE)
    completed = models.BooleanField(null=False, default=models.NOT_PROVIDED)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_earned = models.IntegerField(null=False, default=models.NOT_PROVIDED)

    class Meta:
        unique_together = ['user', 'study_material', 'milestone']

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_url = models.URLField()
    xp_requirement = models.IntegerField()

    def __str__(self) ->str:
        return str(self.name)

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']