import os
import requests
import json
from typing import List, Dict
from datetime import datetime


class AILetterGenerator:
    """
    Generates personalized AI insights and letters using Google Gemini API
    """
    
    def __init__(self):
        # Use your Gemini API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # FIXED: Check if key is valid (not None, not empty, not placeholder)
        if not self.api_key or self.api_key == 'YOUR_GEMINI_KEY_HERE':
            print("⚠️ Warning: GEMINI_API_KEY not found. AI insights will be limited.")
            self.use_api = False
        else:
            self.use_api = True
            # Gemini API endpoint - Using gemini-2.0-flash (fastest and most stable)
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            self.headers = {
                "Content-Type": "application/json"
            }
            print("✅ Gemini API initialized successfully!")
    
    def generate_weekly_summary(self, entries: List[Dict]) -> str:
        """
        Generate a weekly emotional summary
        
        Args:
            entries: List of journal entries with emotion data
            
        Returns:
            Weekly summary text
        """
        if not entries:
            return "You haven't written any entries this week. Start journaling to see your summary!"
        
        if not self.use_api:
            return self._get_fallback_summary(entries)
        
        # Prepare context
        context = self._prepare_weekly_context(entries)
        
        prompt = f"""You are an empathetic emotional wellness companion. Write a warm, supportive 3-paragraph weekly summary based on these journal entries:

{context}

Focus on:
1. Emotional patterns you notice
2. Positive moments and growth
3. Encouragement and perspective

Keep it warm and supportive. Use "you" to speak directly to the person. Write in a caring, friendly tone."""

        try:
            response = self._call_gemini_api(prompt)
            return response if response else self._get_fallback_summary(entries)
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return self._get_fallback_summary(entries)
    
    def generate_future_letter(self, entries: List[Dict], months_ahead: int = 3) -> str:
        """
        Generate a letter to future self
        
        Args:
            entries: Recent journal entries
            months_ahead: How many months in the future
            
        Returns:
            Letter text
        """
        if not entries:
            return "Start writing to unlock letters to your future self!"
        
        if not self.use_api:
            return self._get_fallback_letter(entries, months_ahead)
        
        context = self._prepare_letter_context(entries)
        
        prompt = f"""Write a heartfelt letter to someone's future self, {months_ahead} months from now.

Based on their recent emotional state:
{context}

Start with "Dear Future You," and write 3-4 warm, personal paragraphs that:
- Reflect on their current emotional state
- Remind them of their strengths and resilience
- Offer hope, encouragement, and perspective
- Ask thoughtful questions about their growth

Write as if you're a close friend who deeply cares about them. Be genuine and supportive."""

        try:
            response = self._call_gemini_api(prompt)
            return response if response else self._get_fallback_letter(entries, months_ahead)
            
        except Exception as e:
            print(f"❌ Error generating letter: {e}")
            return self._get_fallback_letter(entries, months_ahead)
    
    def generate_pattern_analysis(self, entries: List[Dict]) -> str:
        """
        Analyze emotional patterns over time
        """
        if len(entries) < 5:
            return "Keep writing! Pattern analysis becomes available after 5 entries."
        
        if not self.use_api:
            return self._get_fallback_pattern_analysis(entries)
        
        context = self._prepare_pattern_context(entries)
        
        prompt = f"""You are an emotional intelligence coach. Analyze these emotional journal patterns and provide 2-3 supportive, insightful paragraphs:

{context}

Identify and discuss:
- Recurring emotional patterns and themes
- Possible triggers or situations affecting mood
- Positive coping mechanisms or growth you observe
- Gentle observations about their emotional journey

Be supportive, insightful, and practical. Avoid being overly clinical."""

        try:
            response = self._call_gemini_api(prompt)
            return response if response else self._get_fallback_pattern_analysis(entries)
            
        except Exception as e:
            print(f"❌ Error generating analysis: {e}")
            return self._get_fallback_pattern_analysis(entries)
    
    def generate_recommendation(self, entries: List[Dict]) -> str:
        """
        Generate personalized recommendations
        """
        if not entries:
            return "Start journaling to get personalized recommendations!"
        
        if not self.use_api:
            return self._get_fallback_recommendations(entries)
        
        context = self._prepare_recommendation_context(entries)
        
        prompt = f"""Based on these emotional patterns, provide 3-4 practical, actionable recommendations:

{context}

Suggest specific activities, practices, or approaches that could help them based on their emotional state. Be:
- Specific and actionable (not vague advice)
- Supportive and encouraging
- Considerate of their current emotional state
- Practical and realistic

Format as a friendly paragraph followed by bullet points."""

        try:
            response = self._call_gemini_api(prompt)
            return response if response else self._get_fallback_recommendations(entries)
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return self._get_fallback_recommendations(entries)
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Call Google Gemini API for text generation
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Generated text response
        """
        try:
            print("🚀 Sending request to Gemini API...")
            print(f"📝 Prompt preview: {prompt[:200]}...")
            
            # Gemini API request format
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"📩 API Response Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.text[:500]}")
                return ""
            
            result = response.json()
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        generated_text = parts[0]["text"].strip()
                        print(f"✅ Generated text: {generated_text[:200]}...")
                        return generated_text
            
            print("⚠️ No valid response from Gemini API")
            return ""
            
        except requests.exceptions.Timeout:
            print("⏱️ Gemini API request timed out")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error calling Gemini API: {e}")
            return ""
        except Exception as e:
            print(f"💥 Unexpected error calling Gemini API: {e}")
            return ""
    
    def _prepare_weekly_context(self, entries: List[Dict]) -> str:
        """Prepare context for weekly summary"""
        context_parts = []
        
        for i, entry in enumerate(entries[-7:], 1):  # Last 7 entries
            date = entry.get('date', 'Unknown')
            primary_emotion = entry.get('primary_emotion', 'neutral')
            sentiment = entry.get('sentiment_polarity', 0)
            preview = entry.get('preview', '')[:100]
            
            context_parts.append(
                f"Entry {i} ({date}):\n"
                f"Primary emotion: {primary_emotion}\n"
                f"Sentiment: {sentiment:.2f}\n"
                f"Preview: {preview}\n"
            )
        
        return "\n".join(context_parts)
    
    def _prepare_letter_context(self, entries: List[Dict]) -> str:
        """Prepare context for future letter"""
        # Get recent entries
        recent = entries[-10:]  # Last 10 entries
        
        # Summarize emotions
        emotions = {}
        for entry in recent:
            primary = entry.get('primary_emotion', 'neutral')
            emotions[primary] = emotions.get(primary, 0) + 1
        
        # Calculate average sentiment
        sentiments = [e.get('sentiment_polarity', 0) for e in recent]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        context = f"""Recent emotional state:
- Most common emotions: {', '.join([f"{k} ({v})" for k, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]])}
- Average sentiment: {avg_sentiment:.2f} (-1 to 1 scale)
- Number of entries: {len(recent)}

Sample recent thoughts:
"""
        
        for entry in recent[-3:]:
            preview = entry.get('preview', '')[:150]
            context += f"- {preview}\n"
        
        return context
    
    def _prepare_pattern_context(self, entries: List[Dict]) -> str:
        """Prepare context for pattern analysis"""
        # Analyze last 30 entries
        recent = entries[-30:]
        
        # Emotion frequency
        emotions = {}
        for entry in recent:
            primary = entry.get('primary_emotion', 'neutral')
            emotions[primary] = emotions.get(primary, 0) + 1
        
        # Sentiment trend
        sentiments = [e.get('sentiment_polarity', 0) for e in recent]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Day patterns
        from collections import Counter
        days = [entry.get('date', '').split('-')[2] if entry.get('date') else '' 
                for entry in recent]
        day_counter = Counter(days)
        
        context = f"""Analysis of last {len(recent)} entries:

Emotion frequency:
{', '.join([f"{k}: {v}" for k, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True)])}

Average sentiment: {avg_sentiment:.2f}

Most active days: {', '.join([f"{k}" for k, v in day_counter.most_common(3)])}

Sentiment range: {min(sentiments):.2f} to {max(sentiments):.2f}
"""
        
        return context
    
    def _prepare_recommendation_context(self, entries: List[Dict]) -> str:
        """Prepare context for recommendations"""
        recent = entries[-7:]  # Last week
        
        # Primary emotions
        emotions = [e.get('primary_emotion', 'neutral') for e in recent]
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        # Average sentiment
        sentiments = [e.get('sentiment_polarity', 0) for e in recent]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        context = f"""Recent week summary:
- Dominant emotion: {dominant_emotion}
- Average sentiment: {avg_sentiment:.2f}
- Entry frequency: {len(recent)} entries in past 7 days
- Emotional variety: {len(set(emotions))} different emotions
"""
        
        return context
    
    def _get_fallback_summary(self, entries: List[Dict]) -> str:
        """Enhanced fallback summary when API fails or unavailable"""
        num_entries = len(entries)
        emotions = [e.get('primary_emotion', 'neutral') for e in entries]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'neutral'
        
        sentiments = [e.get('sentiment_polarity', 0) for e in entries]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Calculate emotional variety
        variety = len(set(emotions))
        
        summary = f"""This week you wrote {num_entries} journal entries, showing great dedication to self-reflection! 

Your emotional journey this week has been centered around {dominant}, which appeared in {emotion_counts.get(dominant, 0)} entries. """
        
        if avg_sentiment > 0.2:
            summary += "Overall, there's a positive tone to your reflections, which suggests you're finding moments of brightness even in challenging times. "
        elif avg_sentiment < -0.2:
            summary += "Your entries reflect some challenging emotions this week. Remember, it's okay to feel difficult emotions - acknowledging them is the first step to processing them. "
        else:
            summary += "Your emotional state has been fairly balanced this week, showing both ups and downs. "
        
        if variety >= 4:
            summary += "You experienced a wide range of emotions, which is completely normal and human. "
        
        summary += "\n\nEach entry you write is valuable progress in understanding yourself better. Keep going - you're doing great work on your emotional wellness journey!"
        
        return summary
    
    def _get_fallback_pattern_analysis(self, entries: List[Dict]) -> str:
        """Fallback pattern analysis"""
        emotions = [e.get('primary_emotion', 'neutral') for e in entries]
        dominant = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        analysis = f"""Based on your recent {len(entries)} entries, I notice some interesting patterns in your emotional landscape.

{dominant.capitalize()} appears to be a recurring theme in your journal. This emotion has shown up consistently, which might indicate it's connected to ongoing situations in your life. Recognizing this pattern is valuable - it gives you insight into what's affecting you emotionally.

Your entries show genuine self-reflection and emotional awareness. The fact that you're consistently journaling demonstrates a commitment to understanding yourself better, which is a powerful tool for emotional growth and well-being."""
        
        return analysis
    
    def _get_fallback_recommendations(self, entries: List[Dict]) -> str:
        """Fallback recommendations"""
        emotions = [e.get('primary_emotion', 'neutral') for e in entries]
        dominant = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        recommendations = f"""Based on your recent emotional patterns, here are some supportive suggestions:

Since {dominant} has been prominent in your entries, consider activities that help you process this emotion constructively. """
        
        if dominant in ['sadness', 'anxiety', 'fear']:
            recommendations += """
• Practice gentle self-care activities like walking, listening to music, or connecting with supportive friends
• Consider mindfulness or breathing exercises to help manage difficult emotions
• Remember that seeking support from others is a sign of strength, not weakness
• Keep journaling - expressing your feelings is therapeutic"""
        elif dominant in ['anger', 'frustration']:
            recommendations += """
• Channel energy into physical activities or creative outlets
• Practice identifying triggers before they escalate
• Take breaks when you notice tension building
• Express your needs clearly and calmly to others"""
        elif dominant in ['joy', 'love', 'excitement']:
            recommendations += """
• Savor these positive moments and reflect on what brings them about
• Share your happiness with others - joy multiplies when shared
• Document what's working well so you can recreate these feelings
• Use this positive energy to tackle challenges you've been postponing"""
        else:
            recommendations += """
• Continue your journaling practice to build emotional awareness
• Try new activities to discover what brings you fulfillment
• Set small, achievable goals to build momentum
• Connect with others and nurture your relationships"""
        
        return recommendations
    
    def _get_fallback_letter(self, entries: List[Dict], months: int) -> str:
        """Fallback letter when API fails"""
        return f"""Dear Future You,

{months} months from now, you'll look back at this moment and see how much you've grown. Right now, you're taking the time to understand your emotions and process your experiences through journaling.

Whatever challenges you're facing today, remember that you have the strength to work through them. The fact that you're writing and reflecting shows your commitment to personal growth.

Keep going. You're doing great.

With care,
Your Present Self"""