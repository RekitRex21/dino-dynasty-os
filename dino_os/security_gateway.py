"""Security Gateway - API key management and permission gates for Dino Dynasty OS."""

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class APIKey:
    """Represents an API key."""
    key_id: str
    key_hash: str
    name: str
    permissions: List[str]
    created_at: str
    expires_at: Optional[str]
    last_used: Optional[str]
    rate_limit: int  # requests per minute
    enabled: bool


class SecurityGateway:
    """Security gateway for API key management and rate limiting."""
    
    def __init__(self):
        """Initialize the security gateway."""
        self._api_keys: Dict[str, APIKey] = {}
        self._rate_limits: Dict[str, List[float]] = {}  # key_id -> list of timestamps
        self._permissions: Dict[str, List[str]] = {}  # key_id -> permissions

    def create_api_key(self, name: str, permissions: List[str],
                       expires_at: Optional[str] = None,
                       rate_limit: int = 60) -> str:
        """Create a new API key.
        
        Args:
            name: Key name
            permissions: List of permissions
            expires_at: Optional expiry date ISO format
            rate_limit: Requests per minute
            
        Returns:
            The new API key (plain text, shown only once).
        """
        key_id = self._generate_key_id()
        plain_key = self._generate_plain_key()
        key_hash = self._hash_key(plain_key)
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            permissions=permissions,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            last_used=None,
            rate_limit=rate_limit,
            enabled=True
        )
        
        self._api_keys[key_id] = api_key
        self._permissions[key_id] = permissions
        
        return plain_key

    def validate_api_key(self, plain_key: str) -> Optional[APIKey]:
        """Validate an API key.
        
        Args:
            plain_key: The plain text API key
            
        Returns:
            APIKey if valid, None otherwise.
        """
        key_hash = self._hash_key(plain_key)
        
        for api_key in self._api_keys.values():
            if api_key.key_hash == key_hash:
                if not api_key.enabled:
                    return None
                if api_key.expires_at:
                    expires = datetime.fromisoformat(api_key.expires_at)
                    if datetime.utcnow() > expires:
                        return None
                return api_key
        return None

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key.
        
        Args:
            key_id: Key ID to revoke
            
        Returns:
            True if revoked.
        """
        if key_id in self._api_keys:
            self._api_keys[key_id].enabled = False
            return True
        return False

    def check_permission(self, plain_key: str, permission: str) -> bool:
        """Check if an API key has a specific permission.
        
        Args:
            plain_key: The plain text API key
            permission: Permission to check
            
        Returns:
            True if allowed.
        """
        api_key = self.validate_api_key(plain_key)
        if not api_key:
            return False
        return permission in api_key.permissions

    def check_rate_limit(self, plain_key: str) -> bool:
        """Check if request is within rate limit.
        
        Args:
            plain_key: The plain text API key
            
        Returns:
            True if within limit.
        """
        api_key = self.validate_api_key(plain_key)
        if not api_key:
            return False
        
        now = time.time()
        minute_ago = now - 60
        
        if api_key.key_id not in self._rate_limits:
            self._rate_limits[api_key.key_id] = []
        
        # Filter to last minute
        timestamps = [t for t in self._rate_limits[api_key.key_id] if t > minute_ago]
        self._rate_limits[api_key.key_id] = timestamps
        
        if len(timestamps) >= api_key.rate_limit:
            return False
        
        # Add current request
        self._rate_limits[api_key.key_id].append(now)
        
        # Update last used
        api_key.last_used = datetime.utcnow().isoformat()
        
        return True

    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys (without exposing the hash).
        
        Returns:
            List of key info dictionaries.
        """
        return [
            {
                "key_id": key.key_id,
                "name": key.name,
                "permissions": key.permissions,
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "last_used": key.last_used,
                "rate_limit": key.rate_limit,
                "enabled": key.enabled
            }
            for key in self._api_keys.values()
        ]

    def _generate_key_id(self) -> str:
        """Generate a unique key ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _generate_plain_key(self) -> str:
        """Generate a plain text API key."""
        import uuid
        return f"dd_{uuid.uuid4().hex}"

    def _hash_key(self, plain_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(plain_key.encode()).hexdigest()
