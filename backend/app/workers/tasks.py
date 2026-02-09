"""
Celery Tasks for Amarktai Marketing
"""

from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio

from app.db.session import SessionLocal
from app.models.content import Content, ContentStatus
from app.models.user import User
from app.models.webapp import WebApp
from app.models.engagement import CostTracking
from app.workflows.nightly_workflow_v2 import get_nightly_workflow
from app.core.config import settings

@shared_task(bind=True, max_retries=3)
def run_nightly_content_generation(self):
    """
    Nightly task that runs the full content generation pipeline for all users.
    Triggered at 2:00 AM daily.
    """
    print("🌙 Starting nightly content generation...")
    
    db = SessionLocal()
    try:
        # Get all active users
        users = db.query(User).all()
        
        for user in users:
            try:
                # Check if user has webapps
                webapps = db.query(WebApp).filter(
                    WebApp.user_id == user.id
                ).all()
                
                if not webapps:
                    continue
                
                # Check monthly quota
                if user.monthly_content_used >= user.monthly_content_quota:
                    print(f"⏭️ User {user.id} has exceeded monthly quota")
                    continue
                
                # Get user's API keys
                from app.models.user_api_key import UserAPIKey
                api_keys = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user.id,
                    UserAPIKey.is_active == True
                ).all()
                
                user_api_keys = {key.key_name: key.get_decrypted_key() for key in api_keys}
                
                # Generate content for each webapp
                for webapp in webapps:
                    try:
                        # Run workflow
                        workflow = get_nightly_workflow()
                        
                        # Get platforms from user's connected integrations
                        from app.models.user_api_key import UserIntegration
                        integrations = db.query(UserIntegration).filter(
                            UserIntegration.user_id == user.id,
                            UserIntegration.is_connected == True
                        ).all()
                        
                        platforms = [i.platform for i in integrations]
                        
                        if not platforms:
                            # Default platforms if none connected
                            platforms = ["youtube", "tiktok", "instagram", "twitter", "linkedin", "facebook"]
                        
                        # Run the workflow
                        result = asyncio.run(workflow.run(
                            user_id=user.id,
                            webapp_id=webapp.id,
                            webapp_data={
                                "id": webapp.id,
                                "name": webapp.name,
                                "url": webapp.url,
                                "description": webapp.description,
                                "category": webapp.category,
                                "key_features": webapp.key_features,
                                "target_audience": webapp.target_audience
                            },
                            platforms=platforms[:3] if user.plan.value == "free" else platforms,  # Limit for free tier
                            user_api_keys=user_api_keys,
                            user_plan=user.plan.value
                        ))
                        
                        if result.get("success"):
                            # Save generated content to database
                            for content_data in result.get("content", []):
                                new_content = Content(
                                    id=content_data["id"],
                                    user_id=user.id,
                                    webapp_id=webapp.id,
                                    platform=content_data["platform"],
                                    type=content_data["type"],
                                    status=ContentStatus.PENDING,
                                    title=content_data["title"],
                                    caption=content_data["caption"],
                                    hashtags=content_data.get("hashtags", []),
                                    media_urls=content_data.get("media_urls", []),
                                    viral_score=content_data.get("viral_score"),
                                    confidence_score=content_data.get("confidence_score"),
                                    llm_tokens_used=content_data.get("generation_metadata", {}).get("tokens_used", 0),
                                    generation_metadata=content_data.get("generation_metadata", {})
                                )
                                db.add(new_content)
                            
                            # Update user's content count
                            user.monthly_content_used += len(result.get("content", []))
                            
                            # Track costs
                            track_generation_cost.delay(
                                user.id,
                                result.get("cost_estimate", 0),
                                len(result.get("content", []))
                            )
                            
                            print(f"✅ Generated {len(result.get('content', []))} content items for user {user.id}")
                        else:
                            print(f"❌ Workflow failed for user {user.id}: {result.get('error')}")
                            
                    except Exception as e:
                        print(f"❌ Error generating content for webapp {webapp.id}: {e}")
                        continue
                
                db.commit()
                
            except Exception as e:
                print(f"❌ Error processing user {user.id}: {e}")
                continue
        
        print("✅ Nightly content generation complete!")
        return {"status": "success", "users_processed": len(users)}
        
    finally:
        db.close()

@shared_task(bind=True, max_retries=3)
def post_content_to_platform(self, content_id: str, user_id: str):
    """
    Post approved content to the target platform.
    """
    print(f"📤 Posting content {content_id} to platform...")
    
    db = SessionLocal()
    try:
        content = db.query(Content).filter(
            Content.id == content_id,
            Content.user_id == user_id
        ).first()
        
        if not content:
            print(f"❌ Content {content_id} not found")
            return {"status": "error", "message": "Content not found"}
        
        # Get user's platform integration
        from app.models.user_api_key import UserIntegration
        integration = db.query(UserIntegration).filter(
            UserIntegration.user_id == user_id,
            UserIntegration.platform == content.platform,
            UserIntegration.is_connected == True
        ).first()
        
        if not integration:
            print(f"⚠️ No integration found for {content.platform}")
            content.status = ContentStatus.FAILED
            db.commit()
            return {"status": "error", "message": f"No {content.platform} integration"}
        
        # Post to platform (platform-specific implementation)
        platform_post_id = None
        
        try:
            if content.platform == "twitter":
                platform_post_id = post_to_twitter(content, integration)
            elif content.platform == "linkedin":
                platform_post_id = post_to_linkedin(content, integration)
            elif content.platform == "youtube":
                platform_post_id = post_to_youtube(content, integration)
            elif content.platform == "instagram":
                platform_post_id = post_to_instagram(content, integration)
            elif content.platform == "facebook":
                platform_post_id = post_to_facebook(content, integration)
            elif content.platform == "tiktok":
                platform_post_id = post_to_tiktok(content, integration)
            else:
                raise Exception(f"Unsupported platform: {content.platform}")
            
            # Update content status
            content.status = ContentStatus.POSTED
            content.posted_at = datetime.now()
            content.platform_post_id = platform_post_id
            db.commit()
            
            print(f"✅ Content posted successfully: {platform_post_id}")
            return {"status": "success", "platform_post_id": platform_post_id}
            
        except Exception as e:
            print(f"❌ Failed to post: {e}")
            content.status = ContentStatus.FAILED
            db.commit()
            
            # Retry if not max retries
            if self.request.retries < 3:
                raise self.retry(countdown=60 * (self.request.retries + 1))
            
            return {"status": "error", "message": str(e)}
            
    finally:
        db.close()

def post_to_twitter(content: Content, integration) -> str:
    """Post content to Twitter/X."""
    import httpx
    
    access_token = integration.get_access_token()
    
    # Build tweet text
    tweet_text = content.caption
    if content.hashtags:
        tweet_text += " " + " ".join(content.hashtags[:2])  # Twitter: max 2 hashtags
    
    with httpx.Client() as client:
        response = client.post(
            "https://api.twitter.com/2/tweets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"text": tweet_text[:280]}  # Twitter limit
        )
        response.raise_for_status()
        return response.json()["data"]["id"]

def post_to_linkedin(content: Content, integration) -> str:
    """Post content to LinkedIn."""
    import httpx
    
    access_token = integration.get_access_token()
    
    # Get user URN
    with httpx.Client() as client:
        me_response = client.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        me_response.raise_for_status()
        author_urn = f"urn:li:person:{me_response.json()['id']}"
        
        # Create share
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content.caption + "\n\n" + " ".join(content.hashtags[:5])
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = client.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=post_data
        )
        response.raise_for_status()
        return response.headers.get("X-RestLi-Id", "")

def post_to_youtube(content: Content, integration) -> str:
    """Post content to YouTube (Shorts)."""
    # YouTube API requires OAuth2 flow with video upload
    # This is a placeholder - full implementation requires YouTube Data API v3
    return "youtube_placeholder"

def post_to_instagram(content: Content, integration) -> str:
    """Post content to Instagram."""
    # Instagram Graph API requires Facebook connection
    # This is a placeholder
    return "instagram_placeholder"

def post_to_facebook(content: Content, integration) -> str:
    """Post content to Facebook."""
    # Facebook Graph API
    # This is a placeholder
    return "facebook_placeholder"

def post_to_tiktok(content: Content, integration) -> str:
    """Post content to TikTok."""
    # TikTok requires special approval for posting API
    # This is a placeholder
    return "tiktok_placeholder"

@shared_task
def sync_platform_analytics(user_id: str):
    """
    Sync analytics data from all connected platforms.
    """
    print(f"📊 Syncing analytics for user {user_id}...")
    
    db = SessionLocal()
    try:
        # Get user's integrations
        from app.models.user_api_key import UserIntegration
        integrations = db.query(UserIntegration).filter(
            UserIntegration.user_id == user_id,
            UserIntegration.is_connected == True
        ).all()
        
        for integration in integrations:
            try:
                # Sync analytics based on platform
                if integration.platform == "twitter":
                    sync_twitter_analytics(integration, db)
                elif integration.platform == "linkedin":
                    sync_linkedin_analytics(integration, db)
                # Add other platforms...
                
            except Exception as e:
                print(f"❌ Error syncing {integration.platform}: {e}")
                continue
        
        print(f"✅ Analytics sync complete for user {user_id}")
        
    finally:
        db.close()

def sync_twitter_analytics(integration, db: Session):
    """Sync Twitter analytics."""
    import httpx
    
    access_token = integration.get_access_token()
    
    with httpx.Client() as client:
        # Get user's tweets
        response = client.get(
            "https://api.twitter.com/2/users/me/tweets",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "tweet.fields": "public_metrics,created_at",
                "max_results": 100
            }
        )
        response.raise_for_status()
        
        tweets = response.json().get("data", [])
        
        for tweet in tweets:
            # Update content metrics
            content = db.query(Content).filter(
                Content.platform_post_id == tweet["id"]
            ).first()
            
            if content:
                metrics = tweet.get("public_metrics", {})
                content.views = metrics.get("impression_count", 0)
                content.likes = metrics.get("like_count", 0)
                content.comments = metrics.get("reply_count", 0)
                content.shares = metrics.get("retweet_count", 0)
        
        db.commit()

def sync_linkedin_analytics(integration, db: Session):
    """Sync LinkedIn analytics."""
    # LinkedIn analytics API
    pass

@shared_task
def track_generation_cost(user_id: str, cost: float, content_count: int):
    """
    Track AI generation costs for a user.
    """
    db = SessionLocal()
    try:
        # Get or create current month's tracking
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tracking = db.query(CostTracking).filter(
            CostTracking.user_id == user_id,
            CostTracking.billing_period_start == current_month
        ).first()
        
        if not tracking:
            import uuid
            next_month = current_month + timedelta(days=32)
            next_month_start = next_month.replace(day=1)
            
            tracking = CostTracking(
                id=str(uuid.uuid4()),
                user_id=user_id,
                billing_period_start=current_month,
                billing_period_end=next_month_start
            )
            db.add(tracking)
        
        # Update costs
        current_total = float(tracking.total_cost or "0.00")
        tracking.total_cost = str(current_total + cost)
        
        db.commit()
        
        # Check budget alerts
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            budget = float(user.api_cost_budget or "5.00")
            total_used = float(tracking.total_cost or "0.00")
            percent_used = (total_used / budget) * 100
            
            # Send alerts at 50%, 80%, 100%
            if percent_used >= 100 and not tracking.alert_100_sent:
                send_budget_alert.delay(user_id, 100, total_used, budget)
                tracking.alert_100_sent = True
            elif percent_used >= 80 and not tracking.alert_80_sent:
                send_budget_alert.delay(user_id, 80, total_used, budget)
                tracking.alert_80_sent = True
            elif percent_used >= 50 and not tracking.alert_50_sent:
                send_budget_alert.delay(user_id, 50, total_used, budget)
                tracking.alert_50_sent = True
            
            db.commit()
        
    finally:
        db.close()

@shared_task
def send_budget_alert(user_id: str, percent: int, used: float, budget: float):
    """
    Send budget alert email to user.
    """
    print(f"📧 Sending budget alert to user {user_id}: {percent}% used")
    
    # In production, send email via Resend/Brevo
    # For now, just log
    print(f"Budget Alert: ${used:.2f} of ${budget:.2f} used ({percent}%)")

@shared_task
def fetch_platform_engagement():
    """
    Fetch new comments and DMs from all connected platforms.
    Triggered periodically (e.g., every 30 minutes).
    """
    print("📥 Fetching platform engagement...")
    
    db = SessionLocal()
    try:
        # Get all connected integrations
        from app.models.user_api_key import UserIntegration
        integrations = db.query(UserIntegration).filter(
            UserIntegration.is_connected == True
        ).all()
        
        for integration in integrations:
            try:
                if integration.platform == "twitter":
                    fetch_twitter_engagement(integration, db)
                # Add other platforms...
                
            except Exception as e:
                print(f"❌ Error fetching {integration.platform} engagement: {e}")
                continue
        
        print("✅ Engagement fetch complete")
        
    finally:
        db.close()

def fetch_twitter_engagement(integration, db: Session):
    """Fetch Twitter mentions and replies."""
    import httpx
    
    access_token = integration.get_access_token()
    
    with httpx.Client() as client:
        # Get mentions
        response = client.get(
            "https://api.twitter.com/2/users/me/mentions",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "tweet.fields": "author_id,created_at,public_metrics",
                "expansions": "author_id",
                "user.fields": "username,public_metrics",
                "max_results": 100
            }
        )
        response.raise_for_status()
        
        mentions = response.json().get("data", [])
        users = {u["id"]: u for u in response.json().get("includes", {}).get("users", [])}
        
        for mention in mentions:
            # Check if already processed
            from app.models.engagement import EngagementReply
            existing = db.query(EngagementReply).filter(
                EngagementReply.platform_comment_id == mention["id"]
            ).first()
            
            if existing:
                continue
            
            # Create new engagement
            author = users.get(mention.get("author_id"), {})
            
            new_engagement = EngagementReply(
                id=str(__import__('uuid').uuid4()),
                user_id=integration.user_id,
                platform="twitter",
                engagement_type="mention",
                platform_comment_id=mention["id"],
                platform_post_id=mention.get("referenced_tweets", [{}])[0].get("id") if mention.get("referenced_tweets") else None,
                author_name=author.get("username", "Unknown"),
                author_platform_id=mention.get("author_id"),
                original_text=mention["text"],
                received_at=datetime.now(),
                status="pending"
            )
            
            db.add(new_engagement)
        
        db.commit()

@shared_task
def analyze_ab_tests():
    """
    Analyze running A/B tests and declare winners.
    Triggered daily.
    """
    print("🧪 Analyzing A/B tests...")
    
    db = SessionLocal()
    try:
        from app.models.engagement import ABTest
        
        # Get running tests that have been running for at least 24 hours
        running_tests = db.query(ABTest).filter(
            ABTest.status == "running",
            ABTest.started_at <= datetime.now() - timedelta(hours=24)
        ).all()
        
        for test in running_tests:
            try:
                # Calculate winner
                best_variant = None
                best_score = 0
                
                for variant in test.variants:
                    metrics = test.variant_metrics.get(variant["variant_id"], {})
                    
                    # Composite engagement score
                    score = (
                        metrics.get("views", 0) * 0.3 +
                        metrics.get("likes", 0) * 0.3 +
                        metrics.get("comments", 0) * 0.25 +
                        metrics.get("shares", 0) * 0.15
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_variant = variant
                
                if best_variant:
                    # Calculate confidence and improvement
                    baseline_metrics = test.variant_metrics.get("A", {})
                    baseline_score = (
                        baseline_metrics.get("views", 0) * 0.3 +
                        baseline_metrics.get("likes", 0) * 0.3 +
                        baseline_metrics.get("comments", 0) * 0.25 +
                        baseline_metrics.get("shares", 0) * 0.15
                    )
                    
                    improvement = ((best_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
                    
                    # Declare winner if improvement > 10%
                    if improvement > 10:
                        test.winning_variant_id = best_variant["variant_id"]
                        test.confidence_level = str(min(95, 70 + improvement))
                        test.improvement_percent = str(round(improvement, 2))
                        test.status = "completed"
                        test.ended_at = datetime.now()
                        
                        print(f"✅ Declared winner for test {test.id}: Variant {best_variant['variant_id']} (+{improvement:.1f}%)")
                
                # End tests running for more than 7 days
                if test.started_at <= datetime.now() - timedelta(days=7):
                    test.status = "completed"
                    test.ended_at = datetime.now()
                
                db.commit()
                
            except Exception as e:
                print(f"❌ Error analyzing test {test.id}: {e}")
                continue
        
        print("✅ A/B test analysis complete")
        
    finally:
        db.close()
