from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from visualizations.animated_blob_generator import AnimatedMoodBlobGenerator
from .models import (
    JournalEntry, EmotionAnalysis, MoodVisualization, 
    AIInsight, UserProfile
)
from emotions.emotion_analyzer import HybridEmotionAnalyzer as EmotionAnalyzer
from visualizations.chart_generator import VisualizationGenerator
from ai_insights.letter_generator import AILetterGenerator


# ============= Authentication Views =============

def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to EchoVerse! Start your journey.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


# ============= Main Dashboard =============

@login_required
def dashboard_view(request):
    """Main dashboard showing overview"""
    user = request.user
    profile = user.profile
    
    # Get recent entries
    recent_entries = JournalEntry.objects.filter(user=user)[:10]
    
    # Get stats
    total_entries = profile.total_entries
    current_streak = profile.current_streak
    
    # Get this week's emotions
    week_ago = timezone.now() - timedelta(days=7)
    weekly_entries = JournalEntry.objects.filter(
        user=user, 
        created_at__gte=week_ago
    ).select_related('emotion_analysis')
    
    # Emotion distribution
    emotion_counts = {}
    for entry in weekly_entries:
        if hasattr(entry, 'emotion_analysis'):
            emotion = entry.emotion_analysis.primary_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Recent insights
    recent_insights = AIInsight.objects.filter(user=user)[:3]
    
    # Recent visualizations
    recent_viz = MoodVisualization.objects.filter(user=user)[:3]
    
    context = {
        'recent_entries': recent_entries,
        'total_entries': total_entries,
        'current_streak': current_streak,
        'emotion_counts': emotion_counts,
        'recent_insights': recent_insights,
        'recent_viz': recent_viz,
    }
    
    return render(request, 'dashboard/index.html', context)


# ============= Journal Entry Views =============

@login_required
def entry_list_view(request):
    """List all journal entries"""
    entries = JournalEntry.objects.filter(user=request.user).select_related('emotion_analysis')
    
    # Filter by date if provided
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    if date_from:
        entries = entries.filter(created_at__gte=date_from)
    if date_to:
        entries = entries.filter(created_at__lte=date_to)
    
    context = {'entries': entries}
    return render(request, 'journal/entry_list.html', context)



@login_required
def entry_create_view(request):
    """Create new journal entry with ANIMATED MOOD BLOB"""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        
        if not content:
            messages.error(request, 'Please write something in your journal.')
            return render(request, 'journal/entry_form.html')
        
        # Create entry
        entry = JournalEntry.objects.create(
            user=request.user,
            title=title,
            content=content
        )
        
        # Update profile stats
        profile = request.user.profile
        profile.total_entries += 1
        profile.total_words += entry.word_count
        profile.update_streak()  # handles date + logic internally now
        profile.save()

        
        # Analyze emotions
        try:
            from emotions.emotion_analyzer import EmotionAnalyzer
            analyzer = EmotionAnalyzer()
            emotion_data = analyzer.analyze_text(content)
            
            # Create emotion analysis
            analysis = EmotionAnalysis.objects.create(
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
            
            # =====================
            # AUTO-GENERATE EVOLVING MOOD BLOB
            # =====================
            try:
                # Get emotion history (last 30 analyzed entries)
                history_entries = JournalEntry.objects.filter(
                    user=request.user,
                    is_analyzed=True,
                    created_at__lt=entry.created_at
                ).select_related('emotion_analysis').order_by('-created_at')[:30]

                emotion_history = []
                for hist_entry in history_entries:
                    if hasattr(hist_entry, 'emotion_analysis'):
                        hist_analysis = hist_entry.emotion_analysis
                        emotion_history.append({
                            'primary_emotion': hist_analysis.primary_emotion,
                            'primary_emotion_score': hist_analysis.primary_emotion_score,
                            'sentiment_polarity': hist_analysis.sentiment_polarity,
                            'joy': hist_analysis.joy_score,
                            'sadness': hist_analysis.sadness_score,
                            'anger': hist_analysis.anger_score,
                            'fear': hist_analysis.fear_score,
                            'love': hist_analysis.love_score,
                            'anxiety': hist_analysis.anxiety_score,
                            'excitement': hist_analysis.excitement_score,
                        })

                # Generate evolving blob using last image as seed
                blob_generator = AnimatedMoodBlobGenerator()
                latest_viz = MoodVisualization.objects.filter(
                    user=request.user,
                    visualization_type='mood_blob'
                ).order_by('-created_at').first()

                blob_state = None
                if latest_viz and latest_viz.image:
                    try:
                        blob_state = latest_viz.image.path
                    except:
                        pass

                image_buffer = blob_generator.generate_evolution_blob(
                    emotion_history=emotion_history,
                    current_emotion=emotion_data,
                    blob_state=blob_state
                )

                # Update existing blob instead of creating new one
                if latest_viz:
                    latest_viz.end_date = entry.created_at.date()
                    latest_viz.entry_count += 1
                    latest_viz.image.save(
                        f'evolving_blob_{timezone.now().strftime("%Y%m%d_%H%M%S")}.png',
                        ContentFile(image_buffer.read()),
                        save=True
                    )
                    latest_viz.save()
                else:
                    viz = MoodVisualization.objects.create(
                        user=request.user,
                        visualization_type='mood_blob',
                        start_date=entry.created_at.date(),
                        end_date=entry.created_at.date(),
                        entry_count=1
                    )
                    viz.image.save(
                        f'evolving_blob_{entry.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.png',
                        ContentFile(image_buffer.read()),
                        save=True
                    )

                # =====================
                # SAVE STATIC EMOTION CARD (raw snapshot for timeline)
                # =====================
                try:
                    static_generator = AnimatedMoodBlobGenerator()
                    static_image = static_generator.generate_static_snapshot(emotion_data)

                    static_viz = MoodVisualization.objects.create(
                        user=request.user,
                        visualization_type='emotion_card',
                        start_date=entry.created_at.date(),
                        end_date=entry.created_at.date(),
                        entry_count=1
                    )
                    static_viz.image.save(
                        f'emotion_card_{entry.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.png',
                        ContentFile(static_image.read()),
                        save=True
                    )
                except Exception as static_err:
                    print(f"⚠️ Error generating emotion card snapshot: {static_err}")


                messages.success(request, '✨ Journal entry created! Your mood blob evolved beautifully.')
            
            except Exception as viz_error:
                print(f"Error auto-generating animated mood blob: {viz_error}")
                messages.success(request, 'Journal entry created successfully!')

        except Exception as e:
            print(f"Error analyzing emotions: {e}")
            messages.warning(request, 'Entry saved but emotion analysis failed.')
        
        return redirect('entry_detail', pk=entry.pk)
    
    return render(request, 'journal/entry_form.html')


@login_required
def entry_detail_view(request, pk):
    """View single journal entry with emotion analysis"""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    
    # Get emotion analysis if available
    emotion_analysis = None
    emotion_chart_data = None
    
    if hasattr(entry, 'emotion_analysis'):
        emotion_analysis = entry.emotion_analysis
        emotion_chart_data = emotion_analysis.get_emotion_dict()
    
    context = {
        'entry': entry,
        'emotion_analysis': emotion_analysis,
        'emotion_chart_data': json.dumps(emotion_chart_data) if emotion_chart_data else None,
    }
    
    return render(request, 'journal/entry_detail.html', context)


@login_required
def entry_update_view(request, pk):
    """Update journal entry"""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        entry.title = request.POST.get('title', '')
        entry.content = request.POST.get('content', '')
        entry.save()
        
        # Re-analyze emotions
        try:
            analyzer = EmotionAnalyzer()
            emotion_data = analyzer.analyze_text(entry.content)
            
            # Update or create emotion analysis
            if hasattr(entry, 'emotion_analysis'):
                analysis = entry.emotion_analysis
            else:
                analysis = EmotionAnalysis(journal_entry=entry)
            
            analysis.primary_emotion = emotion_data['primary_emotion']
            analysis.primary_emotion_score = emotion_data['primary_emotion_score']
            analysis.joy_score = emotion_data.get('joy', 0)
            analysis.sadness_score = emotion_data.get('sadness', 0)
            analysis.anger_score = emotion_data.get('anger', 0)
            analysis.fear_score = emotion_data.get('fear', 0)
            analysis.surprise_score = emotion_data.get('surprise', 0)
            analysis.disgust_score = emotion_data.get('disgust', 0)
            analysis.neutral_score = emotion_data.get('neutral', 0)
            analysis.love_score = emotion_data.get('love', 0)
            analysis.anxiety_score = emotion_data.get('anxiety', 0)
            analysis.excitement_score = emotion_data.get('excitement', 0)
            analysis.sentiment_polarity = emotion_data['sentiment_polarity']
            analysis.save()
            
        except Exception as e:
            print(f"Error re-analyzing: {e}")
        
        messages.success(request, 'Entry updated successfully!')
        return redirect('entry_detail', pk=entry.pk)
    
    context = {'entry': entry}
    return render(request, 'journal/entry_form.html', context)


@login_required
def entry_delete_view(request, pk):
    """Delete journal entry and update profile stats"""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        # Subtract entry stats before deleting
        profile.total_entries = max(profile.total_entries - 1, 0)
        profile.total_words = max(profile.total_words - entry.word_count, 0)

        # Optional: update streak if deleting today’s last entry
        latest_entry = JournalEntry.objects.filter(user=user).exclude(pk=pk).order_by('-created_at').first()
        if latest_entry:
            profile.last_entry_date = latest_entry.created_at.date()
        else:
            profile.last_entry_date = None

        profile.save()

        entry.delete()
        messages.success(request, 'Entry deleted successfully and stats updated.')
        return redirect('entry_list')

    return render(request, 'journal/entry_confirm_delete.html', {'entry': entry})



# ============= Visualization Views =============

@login_required
def visualizations_view(request):
    """View all visualizations"""
    visualizations = MoodVisualization.objects.filter(user=request.user)
    
    context = {'visualizations': visualizations}
    return render(request, 'visualizations/list.html', context)


@login_required
def generate_visualization_view(request):
    """Generate new visualization"""
    if request.method == 'POST':
        viz_type = request.POST.get('type', 'mood_blob')
        days = int(request.POST.get('days', 7))
        
        # Get entries
        start_date = timezone.now() - timedelta(days=days)
        entries = JournalEntry.objects.filter(
            user=request.user,
            created_at__gte=start_date,
            is_analyzed=True
        ).select_related('emotion_analysis')
        
        if not entries.exists():
            messages.error(request, 'Not enough data to generate visualization.')
            return redirect('visualizations')
        
        try:
            generator = VisualizationGenerator()
            
            if viz_type == 'mood_blob':
                # Use most recent entry
                latest = entries.latest('created_at')
                if hasattr(latest, 'emotion_analysis'):
                    emotion_data = latest.emotion_analysis.get_emotion_dict()
                    emotion_data['primary_emotion'] = latest.emotion_analysis.primary_emotion
                    emotion_data['primary_emotion_score'] = latest.emotion_analysis.primary_emotion_score
                    
                    image_buffer = generator.create_mood_blob(emotion_data, latest.created_at)
            
            elif viz_type == 'emotion_timeline':
                # Prepare data
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
                messages.error(request, 'Invalid visualization type.')
                return redirect('visualizations')
            
            # Save visualization
            viz = MoodVisualization.objects.create(
                user=request.user,
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
            
            messages.success(request, 'Visualization generated successfully!')
            return redirect('visualizations')
            
        except Exception as e:
            print(f"Error generating visualization: {e}")
            messages.error(request, 'Failed to generate visualization.')
            return redirect('visualizations')
    
    context = {
        'viz_types': MoodVisualization.VISUALIZATION_TYPES,
    }
    return render(request, 'visualizations/generate.html', context)


# ============= AI Insights Views =============

@login_required
def insights_view(request):
    """View all AI insights"""
    insights = AIInsight.objects.filter(user=request.user)
    
    context = {'insights': insights}
    return render(request, 'insights/list.html', context)


@login_required
def generate_insight_view(request):
    """Generate AI insight"""
    if request.method == 'POST':
        insight_type = request.POST.get('type', 'weekly_summary')
        
        try:
            generator = AILetterGenerator()
            
            # Get relevant entries
            if insight_type == 'weekly_summary':
                days = 7
                title = 'Weekly Emotional Summary'
            elif insight_type == 'future_letter':
                days = 30
                title = 'Letter to Future You'
            else:
                days = 30
                title = 'Pattern Analysis'
            
            start_date = timezone.now() - timedelta(days=days)
            entries = JournalEntry.objects.filter(
                user=request.user,
                created_at__gte=start_date,
                is_analyzed=True
            ).select_related('emotion_analysis')
            
            # Prepare entry data
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
            
            # Generate content
            if insight_type == 'weekly_summary':
                content = generator.generate_weekly_summary(entry_data)
            elif insight_type == 'future_letter':
                content = generator.generate_future_letter(entry_data)
            else:
                content = generator.generate_pattern_analysis(entry_data)
            
            # Save insight
            insight = AIInsight.objects.create(
                user=request.user,
                insight_type=insight_type,
                title=title,
                content=content,
                period_start=start_date.date(),
                period_end=timezone.now().date()
            )
            
            insight.related_entries.set(entries)
            
            messages.success(request, 'AI insight generated successfully!')
            return redirect('insight_detail', pk=insight.pk)
            
        except Exception as e:
            print(f"Error generating insight: {e}")
            messages.error(request, 'Failed to generate insight.')
            return redirect('insights')
    
    context = {
        'insight_types': AIInsight.INSIGHT_TYPES,
    }
    return render(request, 'insights/generate.html', context)


@login_required
def insight_detail_view(request, pk):
    """View single AI insight"""
    insight = get_object_or_404(AIInsight, pk=pk, user=request.user)
    
    # Mark as read
    if not insight.is_read:
        insight.is_read = True
        insight.save()
    
    context = {'insight': insight}
    return render(request, 'insights/detail.html', context)

# journal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """Display user's profile information"""
    return render(request, 'journal/profile.html', {
        'user': request.user
    })


# journal/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def profile_edit_view(request):
    """Allow user to edit basic profile info like username and email"""
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if username and email:
            user.username = username
            user.email = email
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile_view")
        else:
            messages.error(request, "Please fill out all fields.")

    return render(request, "journal/profile_edit.html", {"user": user})


@login_required
def blob_evolution_view(request):
    """View the evolution of the user's mood blob over time"""
    user = request.user

    # Latest evolving blob (main one)
    latest_blob = MoodVisualization.objects.filter(
        user=user,
        visualization_type='mood_blob'
    ).order_by('-created_at').first()

    # Raw emotion cards (individual snapshots)
    emotion_cards = MoodVisualization.objects.filter(
        user=user,
        visualization_type='emotion_card'
    ).order_by('created_at')  # oldest to newest for timeline

    emotion_card_timeline = []
    for card in emotion_cards:
        entry = JournalEntry.objects.filter(
            user=user,
            created_at__date=card.start_date
        ).select_related('emotion_analysis').first()

        if entry and hasattr(entry, 'emotion_analysis'):
            emotion = entry.emotion_analysis.primary_emotion
            preview = entry.content[:100]
            date = entry.created_at  # ✅ use datetime for ordering + accurate record
        else:
            emotion = 'neutral'
            preview = "No journal text found for this card."
            date = card.created_at  # fallback to when the visualization was made

        emotion_card_timeline.append({
            'card': card,
            'emotion': emotion,
            'date': date,  # ✅ this will be datetime
            'preview': preview,
            'unique_id': f"{card.id}-{emotion}",
        })

    # Sort timeline safely (in case of misalignment)
    emotion_card_timeline = sorted(emotion_card_timeline, key=lambda x: x['date'])

    # Stats
    total_entries = JournalEntry.objects.filter(user=user).count()
    unique_colors = EmotionAnalysis.objects.filter(
        journal_entry__user=user
    ).values_list('primary_emotion', flat=True).distinct().count()

    first_entry = JournalEntry.objects.filter(user=user).order_by('created_at').first()
    days_active = (
        (timezone.now().date() - first_entry.created_at.date()).days + 1
        if first_entry else 0
    )

    context = {
        'latest_blob': latest_blob,
        'emotion_card_timeline': emotion_card_timeline,
        'total_entries': total_entries,
        'unique_colors': unique_colors,
        'days_active': days_active,
    }

    return render(request, 'visualizations/blob_evolution.html', context)



@login_required
def emotion_cards_view(request):
    """Display all static emotion snapshots"""
    cards = MoodVisualization.objects.filter(
        user=request.user,
        visualization_type='emotion_card'
    ).order_by('-created_at')

    return render(request, 'visualizations/emotion_cards.html', {'cards': cards})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MoodVisualization  # adjust import path

@login_required
def delete_visualization_view(request, viz_id):
    viz = get_object_or_404(MoodVisualization, id=viz_id, user=request.user)
    if request.method == 'POST':
        viz.delete()
        messages.success(request, 'Visualization deleted successfully 🧹')
    return redirect('blob_evolution')  # or your blob evolution view name
