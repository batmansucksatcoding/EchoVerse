import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import pandas as pd
from typing import List, Dict


class VisualizationGenerator:
    """
    Generates beautiful visualizations for emotional data
    """
    
    def __init__(self):
        # Set style
        sns.set_style("darkgrid")
        plt.rcParams['figure.facecolor'] = '#1a1a2e'
        plt.rcParams['axes.facecolor'] = '#16213e'
        plt.rcParams['text.color'] = '#eee'
        plt.rcParams['axes.labelcolor'] = '#eee'
        plt.rcParams['xtick.color'] = '#eee'
        plt.rcParams['ytick.color'] = '#eee'
        plt.rcParams['grid.color'] = '#333'
        
        self.emotion_colors = {
            'joy': '#FFD700',
            'sadness': '#4169E1',
            'anger': '#DC143C',
            'fear': '#8B008B',
            'surprise': '#FF6347',
            'disgust': '#556B2F',
            'neutral': '#808080',
            'love': '#FF69B4',
            'anxiety': '#9370DB',
            'excitement': '#FF8C00',
        }
    
    def create_mood_blob(self, emotion_data: Dict, date: datetime) -> BytesIO:
        """
        Create an artistic mood blob based on emotions
        Like a mood ring visualization
        """
        # Create image
        size = (800, 800)
        image = Image.new('RGB', size, color='#1a1a2e')
        draw = ImageDraw.Draw(image)
        
        # Get primary emotion and color
        primary = emotion_data.get('primary_emotion', 'neutral')
        color = self.emotion_colors.get(primary, '#808080')
        
        # Convert hex to RGB
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        # Calculate blob properties based on emotion scores
        emotion_scores = {k: v for k, v in emotion_data.items() 
                         if k in self.emotion_colors}
        
        # Main blob in center
        center_x, center_y = size[0] // 2, size[1] // 2
        base_radius = 200
        
        # Create organic blob shape using multiple circles
        num_points = 12
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        
        # Vary radius based on emotion intensity
        intensity = emotion_data.get('primary_emotion_score', 0.5)
        radius_variation = 50 * intensity
        
        points = []
        for angle in angles:
            radius = base_radius + np.random.uniform(-radius_variation, radius_variation)
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            points.append((int(x), int(y)))
        
        # Draw blob
        draw.polygon(points, fill=color_rgb)
        
        # Add secondary emotion layers
        for emotion, score in sorted(emotion_scores.items(), 
                                     key=lambda x: x[1], reverse=True)[1:4]:
            if score > 0.2:  # Only show if significant
                sec_color = self.emotion_colors.get(emotion, '#808080')
                sec_rgb = tuple(int(sec_color[i:i+2], 16) for i in (1, 3, 5))
                
                # Add transparency effect by blending
                alpha = int(score * 128)
                sec_rgba = sec_rgb + (alpha,)
                
                # Random offset circle
                offset_x = center_x + np.random.randint(-100, 100)
                offset_y = center_y + np.random.randint(-100, 100)
                sec_radius = int(base_radius * score * 0.6)
                
                # Create overlay
                overlay = Image.new('RGBA', size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.ellipse(
                    [offset_x - sec_radius, offset_y - sec_radius,
                     offset_x + sec_radius, offset_y + sec_radius],
                    fill=sec_rgba
                )
                
                image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Apply blur for organic feel
        image = image.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Add glow effect
        glow = image.copy()
        glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
        image = Image.blend(image, glow, alpha=0.3)
        
        # Save to BytesIO
        buffer = BytesIO()
        image.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        
        return buffer
    
    def create_emotion_timeline(self, entries_data: List[Dict]) -> BytesIO:
        """
        Create a timeline chart showing emotion changes over time
        """
        if not entries_data:
            return self._create_empty_chart()
        
        # Prepare data
        df = pd.DataFrame(entries_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot emotion scores over time
        emotions_to_plot = ['joy', 'sadness', 'anger', 'anxiety', 'love']
        
        for emotion in emotions_to_plot:
            if emotion in df.columns:
                ax.plot(df['date'], df[emotion], 
                       label=emotion.capitalize(),
                       color=self.emotion_colors[emotion],
                       linewidth=2,
                       marker='o',
                       markersize=6,
                       alpha=0.8)
        
        # Styling
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Emotion Intensity', fontsize=14, fontweight='bold')
        ax.set_title('Your Emotional Journey', fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Format dates
        fig.autofmt_xdate()
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def create_emotion_radar(self, emotion_data: Dict) -> BytesIO:
        """
        Create a radar/spider chart for emotion distribution
        """
        emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 
                   'love', 'anxiety', 'excitement']
        
        values = [emotion_data.get(e, 0) for e in emotions]
        
        # Number of variables
        num_vars = len(emotions)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#FF69B4')
        ax.fill(angles, values, alpha=0.25, color='#FF69B4')
        
        # Labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([e.capitalize() for e in emotions], fontsize=12)
        ax.set_ylim(0, 1)
        
        # Styling
        ax.set_title('Emotion Distribution', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def create_sentiment_trend(self, entries_data: List[Dict]) -> BytesIO:
        """
        Create a sentiment polarity trend chart
        """
        if not entries_data:
            return self._create_empty_chart()
        
        df = pd.DataFrame(entries_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Create gradient colors based on sentiment
        colors = ['#DC143C' if s < 0 else '#FFD700' 
                 for s in df['sentiment_polarity']]
        
        # Bar chart
        bars = ax.bar(df['date'], df['sentiment_polarity'], 
                     color=colors, alpha=0.7, edgecolor='white', linewidth=0.5)
        
        # Add zero line
        ax.axhline(y=0, color='white', linestyle='--', alpha=0.5, linewidth=1)
        
        # Styling
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Sentiment', fontsize=14, fontweight='bold')
        ax.set_title('Sentiment Trend (Positive vs Negative)', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.set_ylim(-1.1, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format dates
        fig.autofmt_xdate()
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def create_emotion_heatmap(self, entries_data: List[Dict]) -> BytesIO:
        """
        Create a heatmap showing emotion intensity over days
        """
        if not entries_data:
            return self._create_empty_chart()
        
        df = pd.DataFrame(entries_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get emotions
        emotions = ['joy', 'sadness', 'anger', 'fear', 'love', 'anxiety']
        
        # Pivot data
        heatmap_data = df[['date'] + emotions].set_index('date')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Heatmap
        sns.heatmap(heatmap_data.T, cmap='YlOrRd', annot=False, 
                   cbar_kws={'label': 'Intensity'},
                   ax=ax, linewidths=0.5)
        
        # Styling
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Emotion', fontsize=14, fontweight='bold')
        ax.set_title('Emotion Intensity Heatmap', fontsize=18, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def _create_empty_chart(self) -> BytesIO:
        """Create a placeholder chart when no data"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No data available yet\nStart writing to see your emotions!',
               ha='center', va='center', fontsize=16, color='#eee')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e')
        buffer.seek(0)
        plt.close()
        
        return buffer