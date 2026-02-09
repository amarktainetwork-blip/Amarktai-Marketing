"""
Content Performance Predictor
Uses AI to predict how well content will perform before posting
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import random

@dataclass
class PerformancePrediction:
    predicted_views: int
    predicted_engagement: int
    predicted_ctr: float
    confidence_score: float
    risk_level: str  # low, medium, high
    improvement_suggestions: List[str]

class ContentPerformancePredictor:
    """
    Predicts content performance before posting.
    
    This unique feature helps users:
    - Understand expected performance
    - Get improvement suggestions
    - Make data-driven decisions
    """
    
    def __init__(self):
        self.performance_factors = {
            "hook_strength": 0.25,
            "caption_length": 0.15,
            "hashtag_count": 0.10,
            "visual_quality": 0.20,
            "posting_time": 0.15,
            "platform_fit": 0.15
        }
    
    def predict_performance(self, 
                          content: Dict[str, Any],
                          platform: str,
                          historical_data: Dict[str, Any] = None) -> PerformancePrediction:
        """
        Predict how well content will perform.
        
        Args:
            content: Content data (caption, hashtags, etc.)
            platform: Target platform
            historical_data: User's historical performance data
            
        Returns:
            PerformancePrediction with metrics and suggestions
        """
        # Analyze content factors
        scores = self._analyze_content_factors(content, platform)
        
        # Calculate overall score
        overall_score = sum(
            scores[factor] * weight 
            for factor, weight in self.performance_factors.items()
        )
        
        # Predict metrics based on score and historical data
        base_views = historical_data.get("avg_views", 1000) if historical_data else 1000
        base_engagement = historical_data.get("avg_engagement", 100) if historical_data else 100
        base_ctr = historical_data.get("avg_ctr", 5.0) if historical_data else 5.0
        
        predicted_views = int(base_views * (0.5 + overall_score))
        predicted_engagement = int(base_engagement * (0.5 + overall_score))
        predicted_ctr = round(base_ctr * (0.5 + overall_score), 2)
        
        # Determine confidence and risk
        confidence = self._calculate_confidence(scores)
        risk_level = self._determine_risk_level(overall_score, confidence)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(scores, content, platform)
        
        return PerformancePrediction(
            predicted_views=predicted_views,
            predicted_engagement=predicted_engagement,
            predicted_ctr=predicted_ctr,
            confidence_score=round(confidence, 2),
            risk_level=risk_level,
            improvement_suggestions=suggestions
        )
    
    def _analyze_content_factors(self, content: Dict[str, Any], platform: str) -> Dict[str, float]:
        """Analyze various content factors and return scores (0-1)."""
        scores = {}
        
        # Hook strength
        caption = content.get("caption", "")
        hook_words = ["discover", "secret", "revealed", "finally", "stop", "never", "always", "instantly"]
        has_strong_hook = any(word in caption.lower() for word in hook_words)
        scores["hook_strength"] = 0.9 if has_strong_hook else 0.6
        
        # Caption length (platform-specific)
        optimal_lengths = {
            "twitter": (100, 200),
            "instagram": (100, 300),
            "linkedin": (200, 500),
            "tiktok": (50, 150),
            "youtube": (200, 400)
        }
        length_range = optimal_lengths.get(platform, (100, 300))
        caption_len = len(caption)
        if length_range[0] <= caption_len <= length_range[1]:
            scores["caption_length"] = 0.9
        elif caption_len < length_range[0]:
            scores["caption_length"] = 0.6
        else:
            scores["caption_length"] = 0.7
        
        # Hashtag count
        hashtags = content.get("hashtags", [])
        optimal_hashtags = {"instagram": (5, 10), "twitter": (1, 3), "linkedin": (3, 5)}
        optimal_range = optimal_hashtags.get(platform, (3, 8))
        if optimal_range[0] <= len(hashtags) <= optimal_range[1]:
            scores["hashtag_count"] = 0.9
        else:
            scores["hashtag_count"] = 0.6
        
        # Visual quality (assume good if media exists)
        media_urls = content.get("media_urls", [])
        scores["visual_quality"] = 0.9 if media_urls else 0.5
        
        # Posting time (assume optimal)
        scores["posting_time"] = 0.85
        
        # Platform fit
        platform_scores = {
            "tiktok": ["video", "short", "trendy"],
            "instagram": ["visual", "aesthetic", "lifestyle"],
            "twitter": ["concise", "opinion", "thread"],
            "linkedin": ["professional", "insight", "industry"],
            "youtube": ["tutorial", "educational", "detailed"]
        }
        platform_keywords = platform_scores.get(platform, [])
        content_lower = caption.lower()
        matches = sum(1 for kw in platform_keywords if kw in content_lower)
        scores["platform_fit"] = 0.6 + (matches * 0.1)
        
        return scores
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence score based on factor consistency."""
        values = list(scores.values())
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        # Higher consistency = higher confidence
        return max(0.5, 1.0 - variance)
    
    def _determine_risk_level(self, overall_score: float, confidence: float) -> str:
        """Determine risk level based on score and confidence."""
        if overall_score > 0.8 and confidence > 0.7:
            return "low"
        elif overall_score > 0.5 and confidence > 0.5:
            return "medium"
        return "high"
    
    def _generate_suggestions(self, 
                            scores: Dict[str, float], 
                            content: Dict[str, Any],
                            platform: str) -> List[str]:
        """Generate improvement suggestions based on low scores."""
        suggestions = []
        
        if scores["hook_strength"] < 0.7:
            suggestions.append("💡 Add a stronger hook in the first sentence (use words like 'discover', 'secret', 'finally')")
        
        if scores["caption_length"] < 0.7:
            if platform == "twitter":
                suggestions.append("💡 Twitter posts perform best at 100-200 characters")
            else:
                suggestions.append(f"💡 Adjust caption length for optimal {platform} engagement")
        
        if scores["hashtag_count"] < 0.7:
            optimal = {"instagram": "5-10", "twitter": "1-2", "linkedin": "3-5"}
            suggestions.append(f"💡 Use {optimal.get(platform, '3-8')} hashtags for best reach")
        
        if scores["visual_quality"] < 0.7:
            suggestions.append("💡 Add high-quality visuals - posts with images/videos get 2x more engagement")
        
        if scores["platform_fit"] < 0.7:
            platform_tips = {
                "tiktok": "Make it more trendy and entertaining",
                "instagram": "Focus on visual storytelling",
                "twitter": "Be more concise and opinionated",
                "linkedin": "Add more professional insights",
                "youtube": "Make it more educational"
            }
            suggestions.append(f"💡 {platform_tips.get(platform, 'Adjust tone for platform')}")
        
        return suggestions
