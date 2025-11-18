# journal/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry, AIInsight, UserProfile
from ai_insights.letter_generator import AILetterGenerator


@shared_task
def analyze_entry_emotions(entry_id):
    """
    Background task to analyze entry emotions
    """
    from emotions.emotion_analyzer import HybridEmotionAnalyzer as EmotionAnalyzer
    from .models import EmotionAnalysis
    
    try:
        entry = JournalEntry.objects.get(id=entry_id)
        
        if entry.is_analyzed:
            return f"Entry {entry_id} already analyzed"
        
        analyzer = EmotionAnalyzer(prefer_remote=True)
        emotion_data = analyzer.analyze_text(entry.content)
        
        # Create emotion analysis
        EmotionAnalysis.objects.create(
            journal_entry=entry,
            primary_emotion=emotion_data['primary_emotion'],
            primary_emotion_score=emotion_data['primary_emotion_score'],
            joy_score=emotion_data.get('joy', 0),
            sadness_score=emotion_data.get('sadness', 0),
            anger_score=emotion_data.get('anger', 0),
            fear_score=emotion_data.get('fear', 0),
            surprise_score=emotion_data.get('surprise', 0),
            disgust_score=emotion_data.get('disgust', 0),
            neutral_score=emotion_data.get('neutral', 0),
            love_score=emotion_data.get('love', 0),
            anxiety_score=emotion_data.get('anxiety', 0),
            excitement_score=emotion_data.get('excitement', 0),
            sentiment_polarity=emotion_data['sentiment_polarity']
        )
        
        entry.is_analyzed = True
        entry.save()
        
        return f"Successfully analyzed entry {entry_id}"
        
    except JournalEntry.DoesNotExist:
        return f"Entry {entry_id} not found"
    except Exception as e:
        return f"Error analyzing entry {entry_id}: {str(e)}"


@shared_task
def generate_weekly_summaries():
    """
    Generate weekly summaries for all active users
    """
    week_ago = timezone.now() - timedelta(days=7)
    
    # Get users who wrote entries this week
    active_users = JournalEntry.objects.filter(
        created_at__gte=week_ago
    ).values_list('user', flat=True).distinct()
    
    generator = AILetterGenerator()
    summaries_created = 0
    
    for user_id in active_users:
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            
            if not profile.enable_weekly_summaries:
                continue
            
            # Get weekly entries
            entries = JournalEntry.objects.filter(
                user_id=user_id,
                created_at__gte=week_ago,
                is_analyzed=True
            ).select_related('emotion_analysis')
            
            # Prepare data
            entry_data = []
            for entry in entries:
                if hasattr(entry, 'emotion_analysis'):
                    analysis = entry.emotion_analysis
                    entry_data.append({
                        'date': entry.created_at.strftime('%Y-%m-%d'),
                        'primary_emotion': analysis.primary_emotion,
                        'sentiment_polarity': analysis.sentiment_polarity,
                        'preview': entry.preview
                    })
            
            # Generate summary
            content = generator.generate_weekly_summary(entry_data)
            
            # Create insight
            AIInsight.objects.create(
                user_id=user_id,
                insight_type='weekly_summary',
                title='Your Weekly Emotional Summary',
                content=content,
                period_start=week_ago.date(),
                period_end=timezone.now().date()
            )
            
            summaries_created += 1
            
        except Exception as e:
            print(f"Error generating summary for user {user_id}: {e}")
            continue
    
    return f"Generated {summaries_created} weekly summaries"


@shared_task
def generate_monthly_letters():
    """
    Generate monthly letters to future self
    """
    month_ago = timezone.now() - timedelta(days=30)
    
    # Get users who wrote entries this month
    active_users = JournalEntry.objects.filter(
        created_at__gte=month_ago
    ).values_list('user', flat=True).distinct()
    
    generator = AILetterGenerator()
    letters_created = 0
    
    for user_id in active_users:
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            
            if not profile.enable_future_letters:
                continue
            
            # Get monthly entries
            entries = JournalEntry.objects.filter(
                user_id=user_id,
                created_at__gte=month_ago,
                is_analyzed=True
            ).select_related('emotion_analysis')
            
            # Prepare data
            entry_data = []
            for entry in entries:
                if hasattr(entry, 'emotion_analysis'):
                    analysis = entry.emotion_analysis
                    entry_data.append({
                        'date': entry.created_at.strftime('%Y-%m-%d'),
                        'primary_emotion': analysis.primary_emotion,
                        'sentiment_polarity': analysis.sentiment_polarity,
                        'preview': entry.preview
                    })
            
            # Generate letter
            content = generator.generate_future_letter(entry_data, months_ahead=3)
            
            # Create insight
            AIInsight.objects.create(
                user_id=user_id,
                insight_type='future_letter',
                title='Letter to Your Future Self',
                content=content,
                period_start=month_ago.date(),
                period_end=timezone.now().date()
            )
            
            letters_created += 1
            
        except Exception as e:
            print(f"Error generating letter for user {user_id}: {e}")
            continue
    
    return f"Generated {letters_created} future letters"


@shared_task
def generate_visualization_batch(user_id, viz_type, days=30):
    """
    Background task to generate visualizations
    """
    from visualizations.chart_generator import VisualizationGenerator
    from .models import MoodVisualization
    from django.core.files.base import ContentFile
    
    try:
        start_date = timezone.now() - timedelta(days=days)
        
        entries = JournalEntry.objects.filter(
            user_id=user_id,
            created_at__gte=start_date,
            is_analyzed=True
        ).select_related('emotion_analysis')
        
        if not entries.exists():
            return "Not enough data for visualization"
        
        generator = VisualizationGenerator()
        
        # Prepare data based on viz type
        if viz_type == 'emotion_timeline':
            data = []
            for entry in entries:
                if hasattr(entry, 'emotion_analysis'):
                    analysis = entry.emotion_analysis
                    data.append({
                        'date': entry.created_at,
                        'joy': analysis.joy_score,
                        'sadness': analysis.sadness_score,
                        'anger': analysis.anger_score,
                        'anxiety': analysis.anxiety_score,
                        'love': analysis.love_score,
                    })
            
            image_buffer = generator.create_emotion_timeline(data)
        
        elif viz_type == 'sentiment_trend':
            data = []
            for entry in entries:
                if hasattr(entry, 'emotion_analysis'):
                    data.append({
                        'date': entry.created_at,
                        'sentiment_polarity': entry.emotion_analysis.sentiment_polarity
                    })
            
            image_buffer = generator.create_sentiment_trend(data)
        
        else:
            return "Invalid visualization type"
        
        # Save visualization
        viz = MoodVisualization.objects.create(
            user_id=user_id,
            visualization_type=viz_type,
            start_date=start_date.date(),
            end_date=timezone.now().date(),
            entry_count=entries.count()
        )
        
        viz.image.save(
            f'{viz_type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.png',
            ContentFile(image_buffer.read()),
            save=True
        )
        
        return f"Visualization created successfully"
        
    except Exception as e:
        return f"Error creating visualization: {str(e)}"
    

from celery import shared_task
from django.utils import timezone
from .models import JournalEntry, AIInsight, MoodVisualization
from ai_insights.letter_generator import AILetterGenerator
from visualizations.chart_generator import VisualizationGenerator
from django.core.files.base import ContentFile
from datetime import timedelta

@shared_task(bind=True)
def generate_ai_insight_task(self, user_id, insight_type):
    """Async AI insight generator"""
    from django.contrib.auth.models import User
    user = User.objects.get(pk=user_id)
    generator = AILetterGenerator()

    days = 7 if insight_type == 'weekly_summary' else 30
    start_date = timezone.now() - timedelta(days=days)
    entries = JournalEntry.objects.filter(user=user, created_at__gte=start_date, is_analyzed=True).select_related('emotion_analysis')

    entry_data = [{
        'date': e.created_at.strftime('%Y-%m-%d'),
        'primary_emotion': e.emotion_analysis.primary_emotion,
        'sentiment_polarity': e.emotion_analysis.sentiment_polarity,
        'preview': e.preview
    } for e in entries if hasattr(e, 'emotion_analysis')]

    if insight_type == 'weekly_summary':
        content = generator.generate_weekly_summary(entry_data)
        title = 'Weekly Emotional Summary'
    elif insight_type == 'future_letter':
        content = generator.generate_future_letter(entry_data)
        title = 'Letter to Future You'
    else:
        content = generator.generate_pattern_analysis(entry_data)
        title = 'Emotional Pattern Analysis'

    insight = AIInsight.objects.create(
        user=user,
        insight_type=insight_type,
        title=title,
        content=content,
        period_start=start_date.date(),
        period_end=timezone.now().date()
    )
    insight.related_entries.set(entries)
    return {'id': insight.pk}


@shared_task(bind=True)
def generate_visualization_task(self, user_id, viz_type, days=7):
    """Async visualization generator"""
    from django.contrib.auth.models import User
    user = User.objects.get(pk=user_id)
    generator = VisualizationGenerator()

    start_date = timezone.now() - timedelta(days=days)
    entries = JournalEntry.objects.filter(user=user, created_at__gte=start_date, is_analyzed=True).select_related('emotion_analysis')

    if not entries.exists():
        raise ValueError("Not enough data for visualization")

    if viz_type == 'mood_blob':
        latest = entries.latest('created_at')
        data = latest.emotion_analysis.get_emotion_dict()
        data['primary_emotion'] = latest.emotion_analysis.primary_emotion
        data['primary_emotion_score'] = latest.emotion_analysis.primary_emotion_score
        buffer = generator.create_mood_blob(data, latest.created_at)
    else:
        data = [{'date': e.created_at, 'sentiment_polarity': e.emotion_analysis.sentiment_polarity} for e in entries]
        buffer = generator.create_sentiment_trend(data)

    viz = MoodVisualization.objects.create(
        user=user,
        visualization_type=viz_type,
        start_date=start_date.date(),
        end_date=timezone.now().date(),
        entry_count=entries.count()
    )
    viz.image.save(f'{viz_type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.png', ContentFile(buffer.read()), save=True)
    return {'id': viz.pk}
