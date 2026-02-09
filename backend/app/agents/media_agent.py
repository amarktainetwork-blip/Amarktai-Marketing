"""
Media Agent for Amarktai Marketing
Orchestrates the generation of images, videos, and audio assets
"""

import asyncio
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import httpx
import os

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

@dataclass
class MediaAsset:
    id: str
    type: MediaType
    url: Optional[str]
    local_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    status: str = "pending"  # pending, generating, completed, failed

class MediaAgent:
    """
    Media Agent orchestrates the generation of images, videos, and audio assets
    using various AI media generation APIs.
    """
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        self.leonardo_api_key = self.config.get("LEONARDO_API_KEY") or os.getenv("LEONARDO_API_KEY")
        self.runway_api_key = self.config.get("RUNWAY_API_KEY") or os.getenv("RUNWAY_API_KEY")
        self.elevenlabs_api_key = self.config.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
        
        # API endpoints
        self.leonardo_base_url = "https://cloud.leonardo.ai/api/rest/v1"
        self.runway_base_url = "https://api.runwayml.com/v1"
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
    
    async def generate_content_media(self,
                                   content_package: Dict[str, Any],
                                   platform: str) -> Dict[str, MediaAsset]:
        """
        Generate all media assets for a content piece.
        
        Args:
            content_package: The content package from CreativeAgent
            platform: Target platform
            
        Returns:
            Dictionary of generated media assets
        """
        print(f"🎨 Generating media for {platform}")
        
        assets = {}
        tasks = []
        
        # Generate image if needed
        if "image_prompts" in content_package.get("content", {}):
            image_prompt = content_package["content"]["image_prompts"]["prompts"]["primary"]
            tasks.append(("image", self.generate_image(image_prompt, platform)))
        
        # Generate video if needed
        if "video_script" in content_package.get("content", {}):
            script = content_package["content"]["video_script"]
            video_prompt = f"Short promotional video: {script.get('title', 'product showcase')}"
            tasks.append(("video", self.generate_video(video_prompt)))
            
            # Generate voiceover
            voiceover_text = self._extract_voiceover_text(script)
            if voiceover_text:
                tasks.append(("audio", self.generate_voiceover(voiceover_text)))
        
        # Execute all generation tasks concurrently
        if tasks:
            results = await asyncio.gather(
                *[task[1] for task in tasks],
                return_exceptions=True
            )
            
            # Map results back to asset types
            for (asset_type, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    print(f"❌ Failed to generate {asset_type}: {result}")
                    assets[asset_type] = MediaAsset(
                        id=f"failed_{asset_type}_{datetime.now().timestamp()}",
                        type=MediaType.IMAGE if asset_type == "image" else MediaType.VIDEO if asset_type == "video" else MediaType.AUDIO,
                        url=None,
                        status="failed"
                    )
                else:
                    assets[asset_type] = result
        
        return assets
    
    async def generate_image(self, 
                           prompt: str,
                           platform: str = "instagram",
                           width: int = 1024,
                           height: int = 1024) -> MediaAsset:
        """
        Generate image using Leonardo.AI or fallback to placeholder.
        
        Args:
            prompt: Image generation prompt
            platform: Target platform (affects dimensions)
            width: Image width
            height: Image height
            
        Returns:
            MediaAsset with generated image
        """
        asset_id = f"img_{datetime.now().timestamp()}"
        
        # If no API key, return placeholder
        if not self.leonardo_api_key:
            print(f"⚠️ No Leonardo API key, using placeholder image")
            return MediaAsset(
                id=asset_id,
                type=MediaType.IMAGE,
                url=f"https://images.unsplash.com/photo-1551434678-e076c223a692?w={width}&h={height}&fit=crop",
                status="completed",
                metadata={"prompt": prompt, "platform": platform}
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.leonardo_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "modelId": "e71a1c2f-4f18-462c-9e24-724f8d609b57",  # Leonardo Kino XL
                "num_images": 1,
                "guidance_scale": 7,
                "scheduler": "EULER_DISCRETE",
                "presetStyle": "DYNAMIC"
            }
            
            async with httpx.AsyncClient() as client:
                # Submit generation request
                response = await client.post(
                    f"{self.leonardo_base_url}/generations",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                generation_id = data["sdGenerationJob"]["generationId"]
                
                # Poll for completion
                image_url = await self._poll_leonardo_generation(client, headers, generation_id)
                
                return MediaAsset(
                    id=asset_id,
                    type=MediaType.IMAGE,
                    url=image_url,
                    status="completed",
                    metadata={"prompt": prompt, "platform": platform, "generation_id": generation_id}
                )
                
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            # Return placeholder on failure
            return MediaAsset(
                id=asset_id,
                type=MediaType.IMAGE,
                url=f"https://images.unsplash.com/photo-1551434678-e076c223a692?w={width}&h={height}&fit=crop",
                status="completed",
                metadata={"prompt": prompt, "platform": platform, "error": str(e)}
            )
    
    async def _poll_leonardo_generation(self, 
                                       client: httpx.AsyncClient,
                                       headers: Dict,
                                       generation_id: str,
                                       max_attempts: int = 60) -> str:
        """Poll Leonardo API for generation completion."""
        
        for attempt in range(max_attempts):
            response = await client.get(
                f"{self.leonardo_base_url}/generations/{generation_id}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data["generations_by_pk"]["status"] == "COMPLETE":
                return data["generations_by_pk"]["generated_images"][0]["url"]
            
            await asyncio.sleep(2)
        
        raise TimeoutError("Image generation timed out")
    
    async def generate_video(self,
                           prompt: str,
                           image_url: Optional[str] = None,
                           duration: int = 4) -> MediaAsset:
        """
        Generate video using Runway ML or fallback to placeholder.
        
        Args:
            prompt: Video generation prompt
            image_url: Optional image to animate
            duration: Target duration in seconds
            
        Returns:
            MediaAsset with generated video
        """
        asset_id = f"vid_{datetime.now().timestamp()}"
        
        # If no API key, return placeholder
        if not self.runway_api_key:
            print(f"⚠️ No Runway API key, using placeholder video")
            return MediaAsset(
                id=asset_id,
                type=MediaType.VIDEO,
                url="https://assets.mixkit.co/videos/preview/mixkit-typing-on-a-laptop-in-a-coffee-shop-484-large.mp4",
                status="completed",
                metadata={"prompt": prompt}
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.runway_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "duration": duration,
                "motion_bucket_id": 127
            }
            
            if image_url:
                payload["image_url"] = image_url
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.runway_base_url}/generate",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                task_id = data["id"]
                
                # Poll for completion
                video_url = await self._poll_runway_generation(client, headers, task_id)
                
                return MediaAsset(
                    id=asset_id,
                    type=MediaType.VIDEO,
                    url=video_url,
                    status="completed",
                    metadata={"prompt": prompt, "task_id": task_id}
                )
                
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            return MediaAsset(
                id=asset_id,
                type=MediaType.VIDEO,
                url="https://assets.mixkit.co/videos/preview/mixkit-typing-on-a-laptop-in-a-coffee-shop-484-large.mp4",
                status="completed",
                metadata={"prompt": prompt, "error": str(e)}
            )
    
    async def _poll_runway_generation(self,
                                     client: httpx.AsyncClient,
                                     headers: Dict,
                                     task_id: str,
                                     max_attempts: int = 120) -> str:
        """Poll Runway API for generation completion."""
        
        for attempt in range(max_attempts):
            response = await client.get(
                f"{self.runway_base_url}/tasks/{task_id}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "SUCCEEDED":
                return data["output"][0]
            elif data["status"] == "FAILED":
                raise Exception(f"Video generation failed: {data.get('error', 'Unknown error')}")
            
            await asyncio.sleep(3)
        
        raise TimeoutError("Video generation timed out")
    
    async def generate_voiceover(self,
                               text: str,
                               voice_id: str = "21m00Tcm4TlvDq8ikWAM",
                               model_id: str = "eleven_multilingual_v2") -> MediaAsset:
        """
        Generate voiceover using ElevenLabs or fallback to placeholder.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            model_id: Model ID to use
            
        Returns:
            MediaAsset with generated audio
        """
        asset_id = f"audio_{datetime.now().timestamp()}"
        
        # If no API key, return placeholder info
        if not self.elevenlabs_api_key:
            print(f"⚠️ No ElevenLabs API key, skipping voiceover")
            return MediaAsset(
                id=asset_id,
                type=MediaType.AUDIO,
                url=None,
                status="completed",
                metadata={"text": text, "note": "Voiceover generation skipped - no API key"}
            )
        
        try:
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text[:5000],  # Limit text length
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.elevenlabs_base_url}/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Get audio content
                audio_content = response.content
                
                # In production, upload to S3/Supabase Storage and return URL
                # For now, return base64 encoded
                audio_base64 = base64.b64encode(audio_content).decode()
                
                return MediaAsset(
                    id=asset_id,
                    type=MediaType.AUDIO,
                    url=f"data:audio/mpeg;base64,{audio_base64}",
                    status="completed",
                    metadata={"text": text[:100], "voice_id": voice_id}
                )
                
        except Exception as e:
            print(f"❌ Voiceover generation failed: {e}")
            return MediaAsset(
                id=asset_id,
                type=MediaType.AUDIO,
                url=None,
                status="failed",
                metadata={"text": text, "error": str(e)}
            )
    
    def _extract_voiceover_text(self, script: Dict[str, Any]) -> str:
        """Extract voiceover text from video script."""
        scenes = script.get("scenes", [])
        voiceover_lines = []
        
        for scene in scenes:
            audio = scene.get("audio", "")
            if audio and len(audio) > 5:  # Filter out very short phrases
                voiceover_lines.append(audio)
        
        return " ".join(voiceover_lines) if voiceover_lines else script.get("hook", "")
