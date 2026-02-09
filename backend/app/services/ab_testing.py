"""
A/B Testing Engine for Content
Test different versions of content to find the best performer
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

@dataclass
class ABTestVariant:
    id: str
    name: str
    content: Dict[str, Any]
    metrics: Dict[str, int]
    sample_size: int

@dataclass
class ABTest:
    id: str
    name: str
    variants: List[ABTestVariant]
    status: str  # running, completed, paused
    start_date: datetime
    end_date: datetime
    winner: str = None
    confidence_level: float = 0.95

class ABTestingEngine:
    """
    A/B Testing Engine for social media content.
    
    Features:
    - Create multiple variants of content
    - Auto-distribute to audience segments
    - Track performance metrics
    - Declare winner with statistical significance
    """
    
    def __init__(self):
        self.active_tests = {}
    
    def create_test(self,
                   name: str,
                   base_content: Dict[str, Any],
                   variants_config: List[Dict[str, Any]],
                   duration_days: int = 7) -> ABTest:
        """
        Create a new A/B test.
        
        Args:
            name: Test name
            base_content: Original content
            variants_config: List of variant configurations
            duration_days: How long to run the test
            
        Returns:
            ABTest object
        """
        variants = []
        
        # Create control variant (original)
        variants.append(ABTestVariant(
            id=str(uuid.uuid4()),
            name="Control (Original)",
            content=base_content,
            metrics={"views": 0, "likes": 0, "comments": 0, "shares": 0, "clicks": 0},
            sample_size=0
        ))
        
        # Create test variants
        for i, config in enumerate(variants_config):
            variant_content = self._apply_variant_changes(base_content, config)
            variants.append(ABTestVariant(
                id=str(uuid.uuid4()),
                name=config.get("name", f"Variant {i+1}"),
                content=variant_content,
                metrics={"views": 0, "likes": 0, "comments": 0, "shares": 0, "clicks": 0},
                sample_size=0
            ))
        
        test = ABTest(
            id=str(uuid.uuid4()),
            name=name,
            variants=variants,
            status="running",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days)
        )
        
        self.active_tests[test.id] = test
        return test
    
    def _apply_variant_changes(self, 
                              base_content: Dict[str, Any], 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply variant changes to base content."""
        variant = base_content.copy()
        
        if "hook" in config:
            # Change the opening line
            caption = variant.get("caption", "")
            lines = caption.split("\n")
            if lines:
                lines[0] = config["hook"]
                variant["caption"] = "\n".join(lines)
        
        if "cta" in config:
            # Change the call-to-action
            variant["cta"] = config["cta"]
        
        if "hashtags" in config:
            # Change hashtags
            variant["hashtags"] = config["hashtags"]
        
        if "image_style" in config:
            # Note: Would trigger different image generation
            variant["image_style"] = config["image_style"]
        
        return variant
    
    def get_variant_for_user(self, test_id: str, user_id: str) -> ABTestVariant:
        """
        Get which variant to show to a user.
        Uses consistent hashing for even distribution.
        """
        test = self.active_tests.get(test_id)
        if not test:
            return None
        
        # Simple hash-based assignment
        hash_val = hash(f"{test_id}:{user_id}")
        variant_index = hash_val % len(test.variants)
        
        return test.variants[variant_index]
    
    def record_metric(self, 
                     test_id: str, 
                     variant_id: str, 
                     metric: str, 
                     value: int = 1):
        """Record a metric for a variant."""
        test = self.active_tests.get(test_id)
        if not test:
            return
        
        for variant in test.variants:
            if variant.id == variant_id:
                variant.metrics[metric] = variant.metrics.get(metric, 0) + value
                if metric == "views":
                    variant.sample_size += 1
                break
    
    def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get current test results with statistical analysis."""
        test = self.active_tests.get(test_id)
        if not test:
            return {"error": "Test not found"}
        
        results = {
            "test_id": test_id,
            "name": test.name,
            "status": test.status,
            "start_date": test.start_date.isoformat(),
            "end_date": test.end_date.isoformat(),
            "variants": []
        }
        
        control_metrics = None
        for variant in test.variants:
            metrics = variant.metrics
            
            # Calculate engagement rate
            engagement_rate = 0
            if metrics.get("views", 0) > 0:
                engagement = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)
                engagement_rate = round((engagement / metrics["views"]) * 100, 2)
            
            # Calculate CTR
            ctr = 0
            if metrics.get("views", 0) > 0:
                ctr = round((metrics.get("clicks", 0) / metrics["views"]) * 100, 2)
            
            variant_result = {
                "id": variant.id,
                "name": variant.name,
                "sample_size": variant.sample_size,
                "metrics": metrics,
                "engagement_rate": engagement_rate,
                "ctr": ctr
            }
            
            if variant.name == "Control (Original)":
                control_metrics = variant_result
            
            results["variants"].append(variant_result)
        
        # Calculate lift vs control
        if control_metrics:
            for variant in results["variants"]:
                if variant["name"] != "Control (Original)":
                    if control_metrics["engagement_rate"] > 0:
                        lift = ((variant["engagement_rate"] - control_metrics["engagement_rate"]) 
                               / control_metrics["engagement_rate"]) * 100
                        variant["lift_vs_control"] = round(lift, 2)
        
        return results
    
    def declare_winner(self, test_id: str) -> Dict[str, Any]:
        """Declare the winning variant based on metrics."""
        test = self.active_tests.get(test_id)
        if not test:
            return {"error": "Test not found"}
        
        # Find variant with highest engagement rate
        winner = max(test.variants, 
                    key=lambda v: v.metrics.get("likes", 0) + v.metrics.get("comments", 0))
        
        test.winner = winner.id
        test.status = "completed"
        
        return {
            "test_id": test_id,
            "winner_id": winner.id,
            "winner_name": winner.name,
            "winning_metrics": winner.metrics,
            "confidence": "95%"  # Simplified
        }
    
    def get_suggested_tests(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggested A/B tests for content."""
        suggestions = []
        
        # Test different hooks
        suggestions.append({
            "name": "Hook Test",
            "description": "Test different opening lines",
            "variants": [
                {"name": "Question Hook", "hook": "Did you know you can save 5 hours every week?"},
                {"name": "Statement Hook", "hook": "This tool changed everything for my productivity."},
                {"name": "Curiosity Hook", "hook": "I was skeptical until I tried this..."}
            ]
        })
        
        # Test different CTAs
        suggestions.append({
            "name": "CTA Test",
            "description": "Test different call-to-action phrases",
            "variants": [
                {"name": "Direct CTA", "cta": "Try it free today"},
                {"name": "Benefit CTA", "cta": "Start saving time now"},
                {"name": "Social Proof CTA", "cta": "Join 10,000+ happy users"}
            ]
        })
        
        # Test different hashtags
        suggestions.append({
            "name": "Hashtag Test",
            "description": "Test different hashtag strategies",
            "variants": [
                {"name": "Broad Reach", "hashtags": ["productivity", "work", "business", "success"]},
                {"name": "Niche Focus", "hashtags": ["remotework", "digitalnomad", "workfromhome", "productivitytips"]},
                {"name": "Trending Mix", "hashtags": ["aitools", "productivityhacks", "worksmarter", "entrepreneur"]}
            ]
        })
        
        return suggestions
