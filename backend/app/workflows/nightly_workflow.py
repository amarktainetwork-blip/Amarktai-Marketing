"""
Nightly Workflow Orchestrator for Amarktai Marketing
Uses LangGraph to orchestrate the content generation pipeline
"""

from typing import Dict, List, Any, TypedDict, Annotated
from datetime import datetime, timedelta
import asyncio
import uuid
from enum import Enum

# LangGraph imports (when available)
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not available, using simplified workflow")

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowState(TypedDict):
    """State for the nightly workflow"""
    user_id: str
    webapps: List[Dict[str, Any]]
    research_results: Dict[str, Any]
    content_packages: List[Dict[str, Any]]
    media_assets: List[Dict[str, Any]]
    pending_approval: List[Dict[str, Any]]
    errors: List[str]
    current_step: str
    status: str

class NightlyWorkflow:
    """
    Nightly Workflow Orchestrator
    
    This workflow runs every night to:
    1. Research trends and competitors for each webapp
    2. Generate content packages for each platform
    3. Generate media assets (images, videos)
    4. Save content to approval queue
    5. Send notification to user
    """
    
    def __init__(self, 
                 research_agent=None,
                 creative_agent=None,
                 media_agent=None,
                 db_session=None,
                 notification_service=None):
        self.research_agent = research_agent
        self.creative_agent = creative_agent
        self.media_agent = media_agent
        self.db = db_session
        self.notification_service = notification_service
        
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_workflow()
        else:
            self.workflow = None
    
    def _build_workflow(self):
        """Build the LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("fetch_webapps", self._fetch_user_webapps)
        workflow.add_node("research", self._run_research)
        workflow.add_node("generate_content", self._generate_content_packages)
        workflow.add_node("generate_media", self._generate_media)
        workflow.add_node("save_to_db", self._save_pending_content)
        workflow.add_node("send_notification", self._send_approval_notification)
        workflow.add_node("handle_error", self._handle_error)
        
        # Define edges
        workflow.set_entry_point("fetch_webapps")
        
        workflow.add_conditional_edges(
            "fetch_webapps",
            self._check_webapps_exist,
            {
                "has_webapps": "research",
                "no_webapps": END
            }
        )
        
        workflow.add_edge("research", "generate_content")
        workflow.add_edge("generate_content", "generate_media")
        workflow.add_edge("generate_media", "save_to_db")
        workflow.add_edge("save_to_db", "send_notification")
        workflow.add_edge("send_notification", END)
        
        # Error handling
        for node in ["research", "generate_content", "generate_media", "save_to_db"]:
            workflow.add_conditional_edges(
                node,
                self._check_for_errors,
                {
                    "has_errors": "handle_error",
                    "no_errors": None
                }
            )
        
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def run(self, user_id: str) -> Dict[str, Any]:
        """
        Execute the nightly workflow for a user.
        
        Args:
            user_id: The user ID to run the workflow for
            
        Returns:
            Workflow execution results
        """
        print(f"🌙 Starting nightly workflow for user: {user_id}")
        
        if self.workflow and LANGGRAPH_AVAILABLE:
            # Use LangGraph workflow
            initial_state = WorkflowState(
                user_id=user_id,
                webapps=[],
                research_results={},
                content_packages=[],
                media_assets=[],
                pending_approval=[],
                errors=[],
                current_step="init",
                status=WorkflowStatus.PENDING.value
            )
            
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                "user_id": user_id,
                "success": len(result.get("errors", [])) == 0,
                "content_generated": len(result.get("pending_approval", [])),
                "errors": result.get("errors", []),
                "completed_at": datetime.now().isoformat()
            }
        else:
            # Use simplified sequential workflow
            return await self._run_simplified_workflow(user_id)
    
    async def _run_simplified_workflow(self, user_id: str) -> Dict[str, Any]:
        """Run simplified workflow without LangGraph."""
        errors = []
        pending_approval = []
        
        try:
            # Step 1: Fetch webapps
            print("📦 Fetching webapps...")
            webapps = await self._fetch_webapps_from_db(user_id)
            
            if not webapps:
                print("ℹ️ No active webapps found")
                return {
                    "user_id": user_id,
                    "success": True,
                    "content_generated": 0,
                    "message": "No active webapps to process"
                }
            
            # Step 2: Process each webapp
            for webapp in webapps:
                try:
                    print(f"🔄 Processing webapp: {webapp.get('name')}")
                    
                    # Research
                    research = await self.research_agent.research_webapp(webapp)
                    
                    # Get connected platforms
                    platforms = await self._get_connected_platforms(user_id)
                    
                    # Generate content for each platform
                    for platform in platforms:
                        try:
                            # Generate content package
                            content_package = await self.creative_agent.generate_content_package(
                                research_data=research,
                                webapp_data=webapp,
                                platform=platform
                            )
                            
                            # Generate media
                            media_assets = await self.media_agent.generate_content_media(
                                content_package=content_package,
                                platform=platform
                            )
                            
                            # Save to pending approval
                            content_record = await self._save_content_to_db(
                                user_id=user_id,
                                webapp_id=webapp.get("id"),
                                content_package=content_package,
                                media_assets=media_assets
                            )
                            
                            pending_approval.append(content_record)
                            
                        except Exception as e:
                            print(f"❌ Error generating content for {platform}: {e}")
                            errors.append(f"{platform}: {str(e)}")
                
                except Exception as e:
                    print(f"❌ Error processing webapp {webapp.get('name')}: {e}")
                    errors.append(f"webapp {webapp.get('name')}: {str(e)}")
            
            # Send notification
            if pending_approval:
                await self._send_notification(user_id, len(pending_approval))
            
            return {
                "user_id": user_id,
                "success": len(errors) == 0,
                "content_generated": len(pending_approval),
                "errors": errors,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return {
                "user_id": user_id,
                "success": False,
                "content_generated": len(pending_approval),
                "errors": [str(e)],
                "completed_at": datetime.now().isoformat()
            }
    
    # LangGraph node functions
    async def _fetch_user_webapps(self, state: WorkflowState) -> WorkflowState:
        """Fetch active web apps for the user."""
        state["current_step"] = "fetch_webapps"
        
        try:
            webapps = await self._fetch_webapps_from_db(state["user_id"])
            state["webapps"] = webapps
        except Exception as e:
            state["errors"] = [f"Failed to fetch webapps: {str(e)}"]
        
        return state
    
    async def _run_research(self, state: WorkflowState) -> WorkflowState:
        """Run research agent for all webapps."""
        state["current_step"] = "research"
        
        try:
            research_results = {}
            for webapp in state["webapps"]:
                result = await self.research_agent.research_webapp(webapp)
                research_results[webapp["id"]] = result
            
            state["research_results"] = research_results
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Research failed: {str(e)}"]
        
        return state
    
    async def _generate_content_packages(self, state: WorkflowState) -> WorkflowState:
        """Generate content packages using creative agent."""
        state["current_step"] = "generate_content"
        
        try:
            content_packages = []
            platforms = await self._get_connected_platforms(state["user_id"])
            
            for webapp in state["webapps"]:
                research = state["research_results"].get(webapp["id"], {})
                
                for platform in platforms:
                    package = await self.creative_agent.generate_content_package(
                        research_data=research,
                        webapp_data=webapp,
                        platform=platform
                    )
                    content_packages.append(package)
            
            state["content_packages"] = content_packages
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Content generation failed: {str(e)}"]
        
        return state
    
    async def _generate_media(self, state: WorkflowState) -> WorkflowState:
        """Generate media assets for all content packages."""
        state["current_step"] = "generate_media"
        
        try:
            media_assets = []
            
            for package in state["content_packages"]:
                assets = await self.media_agent.generate_content_media(
                    package,
                    package["platform"]
                )
                media_assets.append({
                    "package_id": package.get("id"),
                    "platform": package["platform"],
                    "assets": assets
                })
            
            state["media_assets"] = media_assets
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Media generation failed: {str(e)}"]
        
        return state
    
    async def _save_pending_content(self, state: WorkflowState) -> WorkflowState:
        """Save generated content to database as pending approval."""
        state["current_step"] = "save_to_db"
        
        try:
            pending_approval = []
            
            for package, media in zip(state["content_packages"], state["media_assets"]):
                content_record = await self._save_content_to_db(
                    user_id=state["user_id"],
                    webapp_id=package.get("webapp_id"),
                    content_package=package,
                    media_assets=media["assets"]
                )
                pending_approval.append(content_record)
            
            state["pending_approval"] = pending_approval
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Failed to save content: {str(e)}"]
        
        return state
    
    async def _send_approval_notification(self, state: WorkflowState) -> WorkflowState:
        """Send email notification to user."""
        state["current_step"] = "send_notification"
        
        try:
            if state["pending_approval"]:
                await self._send_notification(
                    state["user_id"],
                    len(state["pending_approval"])
                )
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Notification failed: {str(e)}"]
        
        return state
    
    async def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """Handle workflow errors."""
        print(f"❌ Workflow errors: {state.get('errors', [])}")
        return state
    
    # Conditional edge functions
    def _check_webapps_exist(self, state: WorkflowState) -> str:
        """Check if user has active webapps."""
        if state.get("webapps") and len(state["webapps"]) > 0:
            return "has_webapps"
        return "no_webapps"
    
    def _check_for_errors(self, state: WorkflowState) -> str:
        """Check if there are errors."""
        if state.get("errors") and len(state["errors"]) > 0:
            return "has_errors"
        return "no_errors"
    
    # Helper functions
    async def _fetch_webapps_from_db(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch active webapps from database."""
        # In production, query from database
        # For now, return mock data
        return [
            {
                "id": f"webapp-{i}",
                "name": f"Web App {i}",
                "description": "A great web application",
                "category": "SaaS",
                "target_audience": "Developers",
                "key_features": ["Feature 1", "Feature 2"],
                "is_active": True
            }
            for i in range(1, 3)
        ]
    
    async def _get_connected_platforms(self, user_id: str) -> List[str]:
        """Get connected platforms for user."""
        # In production, query from database
        return ["youtube", "tiktok", "instagram", "twitter", "linkedin"]
    
    async def _save_content_to_db(self,
                                 user_id: str,
                                 webapp_id: str,
                                 content_package: Dict[str, Any],
                                 media_assets: Dict[str, Any]) -> Dict[str, Any]:
        """Save content to database."""
        content_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "webapp_id": webapp_id,
            "platform": content_package["platform"],
            "status": "pending",
            "title": content_package["content"].get("caption", {}).get("text", "")[:100],
            "caption": content_package["content"].get("caption", {}).get("text", ""),
            "hashtags": content_package["content"].get("caption", {}).get("hashtags", []),
            "media_urls": [
                media_assets.get("image", {}).url if media_assets.get("image") else None
            ],
            "scheduled_for": datetime.now() + timedelta(hours=8),
            "created_at": datetime.now().isoformat()
        }
        
        # In production, save to database
        print(f"💾 Saved content: {content_record['id']}")
        return content_record
    
    async def _send_notification(self, user_id: str, content_count: int):
        """Send notification to user."""
        print(f"📧 Sending notification to user {user_id}: {content_count} items ready")
        # In production, use email service like Resend or SendGrid
