from django.contrib import admin
from .models import (
    JournalEntry, EmotionAnalysis, MoodVisualization, 
    AIInsight, UserProfile
)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'word_count', 'is_analyzed']
    list_filter = ['is_analyzed', 'created_at', 'user']
    search_fields = ['title', 'content', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'word_count']
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'title', 'content')
        }),
        ('Metadata', {
            'fields': ('word_count', 'is_analyzed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmotionAnalysis)
class EmotionAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'journal_entry', 'primary_emotion', 
        'primary_emotion_score', 'sentiment_polarity', 'analyzed_at'
    ]
    list_filter = ['primary_emotion', 'analyzed_at']
    search_fields = ['journal_entry__user__username', 'primary_emotion']
    date_hierarchy = 'analyzed_at'
    readonly_fields = ['analyzed_at', 'analysis_version']
    
    fieldsets = (
        ('Primary Emotion', {
            'fields': ('journal_entry', 'primary_emotion', 'primary_emotion_score', 'sentiment_polarity')
        }),
        ('Emotion Breakdown', {
            'fields': (
                'joy_score', 'sadness_score', 'anger_score', 'fear_score',
                'surprise_score', 'disgust_score', 'neutral_score',
                'love_score', 'anxiety_score', 'excitement_score'
            ),
            'classes': ('collapse',)
        }),
        ('Analysis Metadata', {
            'fields': ('analyzed_at', 'analysis_version'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MoodVisualization)
class MoodVisualizationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'visualization_type', 'start_date', 
        'end_date', 'entry_count', 'created_at'
    ]
    list_filter = ['visualization_type', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def get_image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" />'
        return '-'
    
    get_image_preview.short_description = 'Preview'
    get_image_preview.allow_tags = True


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'insight_type', 'title', 
        'generated_at', 'is_read'
    ]
    list_filter = ['insight_type', 'is_read', 'generated_at']
    search_fields = ['user__username', 'title', 'content']
    date_hierarchy = 'generated_at'
    readonly_fields = ['generated_at']
    filter_horizontal = ['related_entries']
    
    fieldsets = (
        ('Insight Information', {
            'fields': ('user', 'insight_type', 'title', 'content')
        }),
        ('Related Data', {
            'fields': ('related_entries', 'period_start', 'period_end')
        }),
        ('Metadata', {
            'fields': ('generated_at', 'is_read'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'current_streak', 'longest_streak', 
        'total_entries', 'total_words', 'joined_at'
    ]
    list_filter = ['notification_frequency', 'joined_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['joined_at', 'last_entry_date']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': (
                'timezone', 'preferred_visualization',
                'enable_weekly_summaries', 'enable_future_letters',
                'notification_frequency'
            )
        }),
        ('Statistics', {
            'fields': (
                'current_streak', 'longest_streak',
                'total_entries', 'total_words'
            )
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'last_entry_date'),
            'classes': ('collapse',)
        }),
    )