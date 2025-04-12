from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError

# Models
from ..models.study_materials import (
    ScrapedContent,
    StudyMaterial,
    KeyConcept,
    StudyMilestone,
    BookmarkedInsight
)

# Services
from ..services.content_scraper import ContentScraper
from ..services.content_processor import ContentProcessor
from ..services.gamification import GamificationService


class StudyMaterialView(LoginRequiredMixin, View):
    template_name = 'core/study_material.html'
    
    def get(self, request, material_id=None):
        if material_id:
            # Load specific study material and user progress
            material = get_object_or_404(StudyMaterial, id=material_id)
            progress_stats = GamificationService.get_progress_stats(request.user)

            return render(request, self.template_name, {
                'material': material,
                'progress': progress_stats
            })
        
        # Default render for view without specific material
        return render(request, self.template_name)

    def post(self, request):
        try:
            # Get input from form: either URL or PDF
            url = request.POST.get('url')
            pdf_file = request.FILES.get('pdf_file')
            
            if not url and not pdf_file:
                raise ValidationError('Please provide either a URL or a PDF file.')

            # Scrape and extract content
            if url:
                raw_content = ContentScraper.process_content(url)
            else:
                raw_content = ContentScraper.process_content(pdf_file, is_pdf=True)
            
            # Save raw scraped content
            scraped_content = ScrapedContent.objects.create(
                url=url or '',
                title=raw_content['title'],
                raw_content=raw_content['content'],
                source_type=raw_content['source_type']
            )
            
            # Process content to extract structured study data
            processed = ContentProcessor.process_content(
                content=raw_content['content'],
                title=raw_content['title']
            )
            
            # Save StudyMaterial entry
            study_material = StudyMaterial.objects.create(
                scraped_content=scraped_content,
                title=processed.title,
                summary=processed.summary,
                eli5_explanation=processed.eli5_explanation,
                study_duration=processed.estimated_duration
            )
            
            # Save Key Concepts
            for concept in processed.key_concepts:
                KeyConcept.objects.create(
                    study_material=study_material,
                    concept=concept['concept'],
                    definition=concept['definition']
                )
            
            # Save Milestones
            for i, milestone in enumerate(processed.study_milestones, 1):
                StudyMilestone.objects.create(
                    study_material=study_material,
                    title=milestone['title'],
                    description=milestone['description'],
                    order=i,
                    xp_reward=milestone['xp_reward']
                )
            
            # Save Bookmarked Insights
            for insight in processed.bookmarked_insights:
                BookmarkedInsight.objects.create(
                    study_material=study_material,
                    content=insight['content'],
                    importance_level=insight['importance_level']
                )
            
            # Award XP to user for creating material
            GamificationService.award_xp(request.user, 'read_material')
            
            return JsonResponse({
                'status': 'success',
                'material_id': study_material.id,
                'message': 'Study material created successfully.'
            })

        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

        except Exception as e:
            print("[Error] StudyMaterialView POST:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to process content.'
            }, status=500)


class StudyMilestoneView(LoginRequiredMixin, View):
    def post(self, request, milestone_id):
        milestone = get_object_or_404(StudyMilestone, id=milestone_id)

        try:
            result = GamificationService.complete_milestone(request.user, milestone)

            return JsonResponse({
                'status': 'success',
                'xp_earned': result['xp_earned'],
                'new_badges': result['new_badges']
            })

        except Exception as e:
            print("[Error] StudyMilestoneView POST:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to complete milestone.'
            }, status=500)
