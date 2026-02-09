"""
User API Keys Model - Stores encrypted user-provided API keys
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import json
from cryptography.fernet import Fernet
from app.core.config import settings

# Initialize encryption
fernet = Fernet(settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')[:32]) if settings.ENCRYPTION_KEY else None

class UserAPIKey(Base):
    __tablename__ = "user_api_keys"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    key_name = Column(String, nullable=False)  # e.g., 'groq', 'huggingface', 'leonardo'
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(String, default="0")  # Track usage
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def encrypt_key(key_value: str) -> str:
        """Encrypt an API key."""
        if fernet:
            return fernet.encrypt(key_value.encode()).decode()
        return key_value  # Fallback - not recommended for production
    
    @staticmethod
    def decrypt_key(encrypted_value: str) -> str:
        """Decrypt an API key."""
        if fernet:
            return fernet.decrypt(encrypted_value.encode()).decode()
        return encrypted_value
    
    def get_decrypted_key(self) -> str:
        """Get the decrypted API key value."""
        return self.decrypt_key(self.encrypted_key)


class UserIntegration(Base):
    """Stores OAuth2 tokens and connection status for social platforms."""
    __tablename__ = "user_integrations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String, nullable=False)  # youtube, tiktok, instagram, facebook, twitter, linkedin
    
    # OAuth2 tokens (encrypted)
    encrypted_access_token = Column(Text, nullable=True)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Connection status
    is_connected = Column(Boolean, default=False)
    connected_at = Column(DateTime(timezone=True), nullable=True)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Platform-specific data
    platform_user_id = Column(String, nullable=True)  # User's ID on the platform
    platform_username = Column(String, nullable=True)
    platform_data = Column(Text, nullable=True)  # JSON string of additional platform data
    
    # Permissions/scopes granted
    scopes = Column(Text, nullable=True)  # JSON array of granted scopes
    
    # Auto-post settings
    auto_post_enabled = Column(Boolean, default=False)
    auto_reply_enabled = Column(Boolean, default=False)
    low_risk_auto_reply = Column(Boolean, default=False)  # Auto-reply to simple comments
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    
    def get_access_token(self) -> str:
        """Get decrypted access token."""
        if self.encrypted_access_token and fernet:
            return fernet.decrypt(self.encrypted_access_token.encode()).decode()
        return self.encrypted_access_token
    
    def get_refresh_token(self) -> str:
        """Get decrypted refresh token."""
        if self.encrypted_refresh_token and fernet:
            return fernet.decrypt(self.encrypted_refresh_token.encode()).decode()
        return self.encrypted_refresh_token
    
    @staticmethod
    def encrypt_token(token: str) -> str:
        """Encrypt a token."""
        if fernet and token:
            return fernet.encrypt(token.encode()).decode()
        return token
