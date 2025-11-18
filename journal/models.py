from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JournalEntry(models.Model):
    """Main journal entry model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(help_text="Write your thoughts here...")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    word_count = models.IntegerField(default=0)
    is_analyzed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Calculate word count
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)
    
    @property
    def preview(self):
        """Return first 100 characters"""
        return self.content[:100] + '...' if len(self.content) > 100 else self.content


class EmotionAnalysis(models.Model):
    """Stores emotion analysis for each journal entry"""
    EMOTION_CHOICES = [
        ('joy', 'Joy'),
        ('sadness', 'Sadness'),
        ('anger', 'Anger'),
        ('fear', 'Fear'),
        ('surprise', 'Surprise'),
        ('disgust', 'Disgust'),
        ('neutral', 'Neutral'),
        ('love', 'Love'),
        ('anxiety', 'Anxiety'),
        ('excitement', 'Excitement'),
    ]
    
    journal_entry = models.OneToOneField(
        JournalEntry, 
        on_delete=models.CASCADE, 
        related_name='emotion_analysis'
    )
    
    # Primary emotion
    primary_emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    primary_emotion_score = models.FloatField(help_text="Confidence score 0-1")
    
    # Emotion breakdown (stored as JSON-like structure)
    joy_score = models.FloatField(default=0.0)
    sadness_score = models.FloatField(default=0.0)
    anger_score = models.FloatField(default=0.0)
    fear_score = models.FloatField(default=0.0)
    surprise_score = models.FloatField(default=0.0)
    disgust_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    love_score = models.FloatField(default=0.0)
    anxiety_score = models.FloatField(default=0.0)
    excitement_score = models.FloatField(default=0.0)
    
    # Sentiment polarity
    sentiment_polarity = models.FloatField(
        help_text="Range from -1 (negative) to 1 (positive)"
    )
    
    # Analysis metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)
    analysis_version = models.CharField(max_length=20, default='1.0')
    
    class Meta:
        verbose_name = 'Emotion Analysis'
        verbose_name_plural = 'Emotion Analyses'
    
    def __str__(self):
        return f"{self.journal_entry.user.username} - {self.primary_emotion} ({self.primary_emotion_score:.2f})"
    
    def get_emotion_dict(self):
        """Return all emotions as dictionary"""
        return {
            'joy': self.joy_score,
            'sadness': self.sadness_score,
            'anger': self.anger_score,
            'fear': self.fear_score,
            'surprise': self.surprise_score,
            'disgust': self.disgust_score,
            'neutral': self.neutral_score,
            'love': self.love_score,
            'anxiety': self.anxiety_score,
            'excitement': self.excitement_score,
        }
    
    def get_color_code(self):
        """Return color based on primary emotion"""
        color_map = {
            'joy': '#FFD700',      # Gold
            'sadness': '#4169E1',  # Royal Blue
            'anger': '#DC143C',    # Crimson
            'fear': '#8B008B',     # Dark Magenta
            'surprise': '#FF6347', # Tomato
            'disgust': '#556B2F',  # Dark Olive Green
            'neutral': '#808080',  # Gray
            'love': '#FF69B4',     # Hot Pink
            'anxiety': '#9370DB',  # Medium Purple
            'excitement': '#FF8C00', # Dark Orange
        }
        return color_map.get(self.primary_emotion, '#808080')


class MoodVisualization(models.Model):
    """Stores generated visualizations"""
    VISUALIZATION_TYPES = [
        ('mood_blob', 'Mood Blob'),
        ('emotion_chart', 'Emotion Chart'),
        ('timeline', 'Timeline'),
        ('heatmap', 'Heatmap'),
        ('word_cloud', 'Word Cloud'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visualizations')
    visualization_type = models.CharField(max_length=20, choices=VISUALIZATION_TYPES)
    
    # Time range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Image file
    image = models.ImageField(upload_to='visualizations/%Y/%m/')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    entry_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mood Visualization'
        verbose_name_plural = 'Mood Visualizations'
    
    def __str__(self):
        return f"{self.user.username} - {self.visualization_type} - {self.start_date}"


class AIInsight(models.Model):
    """Stores AI-generated insights and letters"""
    INSIGHT_TYPES = [
        ('weekly_summary', 'Weekly Summary'),
        ('future_letter', 'Letter to Future Self'),
        ('pattern_analysis', 'Pattern Analysis'),
        ('recommendation', 'Recommendation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    
    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Related entries
    related_entries = models.ManyToManyField(JournalEntry, related_name='insights')
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Time context
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'AI Insight'
        verbose_name_plural = 'AI Insights'
    
    def __str__(self):
        return f"{self.user.username} - {self.insight_type} - {self.generated_at.strftime('%Y-%m-%d')}"


class UserProfile(models.Model):
    """Extended user profile for preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Preferences
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    preferred_visualization = models.CharField(max_length=20, default='mood_blob')
    
    # Settings
    enable_weekly_summaries = models.BooleanField(default=True)
    enable_future_letters = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('never', 'Never'),
        ],
        default='weekly'
    )
    
    # Streaks and statistics
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_entries = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    last_entry_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_streak(self):
        """Update streak logic reliably."""
        from datetime import timedelta
        today = timezone.now().date()

        # First ever entry
        if not self.last_entry_date:
            self.current_streak = 1
            self.last_entry_date = today
            self.longest_streak = 1
            self.save()
            return

        days_diff = (today - self.last_entry_date).days

        if days_diff == 0:
            # Already wrote today — do nothing
            pass
        elif days_diff == 1:
            # Continued streak
            self.current_streak += 1
        else:
            # Missed one or more days — reset streak
            self.current_streak = 1

        # Update longest streak if needed
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        # Always update last entry date
        self.last_entry_date = today
        self.save()
