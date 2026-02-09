"""
Smart Scheduling Service
Finds optimal posting times based on audience activity and historical performance
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

@dataclass
class OptimalTimeSlot:
    day: str
    time: str
    score: float
    reason: str

@dataclass
class AudienceInsight:
    peak_hours: List[str]
    active_days: List[str]
    timezone: str
    demographics: Dict[str, Any]

class SmartScheduler:
    """
    Smart Scheduling Service
    
    Features:
    - Analyzes audience activity patterns
    - Learns from historical post performance
    - Suggests optimal posting times per platform
    - Considers timezone and demographics
    """
    
    def __init__(self):
        self.platform_optimal_times = {
            "youtube": {
                "weekday": ["14:00", "16:00", "19:00"],
                "weekend": ["10:00", "14:00", "18:00"]
            },
            "tiktok": {
                "weekday": ["07:00", "12:00", "19:00", "21:00"],
                "weekend": ["09:00", "11:00", "19:00", "20:00"]
            },
            "instagram": {
                "weekday": ["11:00", "13:00", "17:00", "19:00"],
                "weekend": ["10:00", "14:00", "18:00"]
            },
            "facebook": {
                "weekday": ["09:00", "13:00", "15:00"],
                "weekend": ["12:00", "13:00", "14:00"]
            },
            "twitter": {
                "weekday": ["08:00", "12:00", "17:00"],
                "weekend": ["09:00", "11:00", "15:00"]
            },
            "linkedin": {
                "weekday": ["08:00", "12:00", "17:00"],
                "weekend": []  # LinkedIn is weekday-focused
            }
        }
    
    def get_optimal_posting_times(self,
                                 platform: str,
                                 user_timezone: str = "UTC",
                                 historical_data: Dict[str, Any] = None) -> List[OptimalTimeSlot]:
        """
        Get optimal posting times for a platform.
        
        Args:
            platform: Target platform
            user_timezone: User's timezone
            historical_data: Historical performance data
            
        Returns:
            List of optimal time slots with scores
        """
        platform_times = self.platform_optimal_times.get(platform, {})
        
        slots = []
        
        # Add platform-recommended times
        for day_type in ["weekday", "weekend"]:
            times = platform_times.get(day_type, [])
            for time in times:
                score = self._calculate_time_score(platform, time, day_type, historical_data)
                slots.append(OptimalTimeSlot(
                    day=day_type,
                    time=time,
                    score=score,
                    reason=f"Peak {platform} activity time"
                ))
        
        # Sort by score
        slots.sort(key=lambda x: x.score, reverse=True)
        
        return slots[:5]  # Return top 5
    
    def _calculate_time_score(self,
                             platform: str,
                             time: str,
                             day_type: str,
                             historical_data: Dict[str, Any] = None) -> float:
        """Calculate a score for a time slot."""
        base_score = 0.7
        
        if historical_data:
            # Check if this time performed well historically
            past_posts = historical_data.get("posts_by_time", {}).get(time, [])
            if past_posts:
                avg_engagement = sum(p.get("engagement", 0) for p in past_posts) / len(past_posts)
                base_score += min(0.2, avg_engagement / 1000)
        
        # Boost certain times
        if platform == "linkedin" and day_type == "weekday":
            if time in ["08:00", "12:00", "17:00"]:
                base_score += 0.1
        
        return min(1.0, base_score)
    
    def schedule_content(self,
                        content: Dict[str, Any],
                        platform: str,
                        preferences: Dict[str, Any] = None) -> datetime:
        """
        Schedule content for optimal time.
        
        Args:
            content: Content to schedule
            platform: Target platform
            preferences: User preferences (timezone, etc.)
            
        Returns:
            Scheduled datetime
        """
        user_timezone = preferences.get("timezone", "UTC") if preferences else "UTC"
        
        # Get optimal times
        optimal_times = self.get_optimal_posting_times(platform, user_timezone)
        
        if not optimal_times:
            # Default to tomorrow 10 AM
            return datetime.now() + timedelta(days=1, hours=10)
        
        # Pick the best time
        best_slot = optimal_times[0]
        
        # Calculate next occurrence
        now = datetime.now()
        hour, minute = map(int, best_slot.time.split(":"))
        
        if best_slot.day == "weekday":
            # Find next weekday
            days_ahead = 0 if now.weekday() < 5 else (7 - now.weekday())
        else:
            # Find next weekend day
            days_ahead = (5 - now.weekday()) % 7  # Saturday
        
        scheduled = now + timedelta(days=days_ahead)
        scheduled = scheduled.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If time has passed today, move to next occurrence
        if scheduled < now:
            scheduled += timedelta(days=7 if best_slot.day == "weekday" else 1)
        
        return scheduled
    
    def analyze_audience_activity(self, 
                                 platform: str,
                                 follower_data: Dict[str, Any] = None) -> AudienceInsight:
        """
        Analyze audience activity patterns.
        
        Args:
            platform: Target platform
            follower_data: Follower demographic data
            
        Returns:
            AudienceInsight with activity patterns
        """
        # In production, this would use platform APIs
        # For now, return platform-typical patterns
        
        patterns = {
            "youtube": {
                "peak_hours": ["14:00-16:00", "19:00-21:00"],
                "active_days": ["Thursday", "Friday", "Saturday", "Sunday"],
                "timezone": "America/New_York"
            },
            "tiktok": {
                "peak_hours": ["07:00-09:00", "12:00-13:00", "19:00-22:00"],
                "active_days": ["Tuesday", "Thursday", "Friday"],
                "timezone": "America/New_York"
            },
            "instagram": {
                "peak_hours": ["11:00-13:00", "17:00-19:00"],
                "active_days": ["Wednesday", "Friday", "Saturday"],
                "timezone": "America/New_York"
            },
            "twitter": {
                "peak_hours": ["08:00-10:00", "12:00-14:00", "17:00-19:00"],
                "active_days": ["Tuesday", "Wednesday", "Thursday"],
                "timezone": "America/New_York"
            },
            "linkedin": {
                "peak_hours": ["08:00-10:00", "12:00-14:00"],
                "active_days": ["Tuesday", "Wednesday", "Thursday"],
                "timezone": "America/New_York"
            }
        }
        
        pattern = patterns.get(platform, patterns["instagram"])
        
        return AudienceInsight(
            peak_hours=pattern["peak_hours"],
            active_days=pattern["active_days"],
            timezone=pattern["timezone"],
            demographics={
                "age_groups": ["25-34", "35-44"],
                "top_locations": ["United States", "United Kingdom", "Canada"]
            }
        )
    
    def get_weekly_schedule(self,
                           platforms: List[str],
                           posts_per_day: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a weekly posting schedule.
        
        Args:
            platforms: List of platforms to schedule for
            posts_per_day: Number of posts per day
            
        Returns:
            Weekly schedule by day
        """
        schedule = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            schedule[day] = []
            
            # Distribute posts across platforms
            for i in range(posts_per_day):
                platform = platforms[i % len(platforms)]
                
                # Get optimal times for this platform
                optimal_times = self.get_optimal_posting_times(platform)
                
                if optimal_times:
                    time_slot = optimal_times[i % len(optimal_times)]
                    
                    schedule[day].append({
                        "platform": platform,
                        "time": time_slot.time,
                        "optimal_score": time_slot.score,
                        "reason": time_slot.reason
                    })
        
        return schedule
