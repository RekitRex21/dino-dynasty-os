"""Channel Manager - Unified interface for all messaging channels."""

from typing import Any, Dict, List, Optional

from .telegram import TelegramChannel
from .discord import DiscordChannel
from .whatsapp import WhatsAppChannel


CHANNEL_TYPES = {
    'telegram': TelegramChannel,
    'discord': DiscordChannel,
    'whatsapp': WhatsAppChannel,
}


class ChannelManager:
    """Manages multiple messaging channel plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize channel manager.
        
        Args:
            config: Channels configuration dict.
        """
        self.config = config
        self.channels: Dict[str, Any] = {}
        self._init_channels()
    
    def _init_channels(self) -> None:
        """Initialize all configured channels."""
        for channel_type, channel_class in CHANNEL_TYPES.items():
            channel_config = self.config.get(channel_type, {})
            if channel_config.get('enabled', False):
                self.channels[channel_type] = channel_class(channel_config)
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all enabled channels.
        
        Returns:
            Dict mapping channel name to connection status.
        """
        results = {}
        for name, channel in self.channels.items():
            results[name] = await channel.connect()
        return results
    
    async def disconnect_all(self) -> None:
        """Disconnect from all channels."""
        for channel in self.channels.values():
            await channel.disconnect()
    
    async def send(self, channel: str, target: str, message: str, **kwargs) -> Optional[str]:
        """Send a message via a specific channel.
        
        Args:
            channel: Channel name (telegram, discord, whatsapp)
            target: Target ID (chat_id, channel_id, phone_number)
            message: Message content
            **kwargs: Additional parameters
            
        Returns:
            Message ID or None on failure.
        """
        if channel not in self.channels:
            return None
        
        return await self.channels[channel].send_message(target, message, **kwargs)
    
    async def broadcast(self, targets: Dict[str, str], message: str) -> Dict[str, Optional[str]]:
        """Broadcast a message to multiple channels.
        
        Args:
            targets: Dict mapping channel name to target ID
            message: Message content
            
        Returns:
            Dict mapping channel name to message ID.
        """
        results = {}
        for channel, target in targets.items():
            if channel in self.channels:
                results[channel] = await self.channels[channel].send_message(target, message)
            else:
                results[channel] = None
        return results
    
    def get_channel(self, name: str) -> Optional[Any]:
        """Get a specific channel by name.
        
        Args:
            name: Channel name
            
        Returns:
            Channel instance or None.
        """
        return self.channels.get(name)
    
    def is_channel_enabled(self, name: str) -> bool:
        """Check if a channel is enabled.
        
        Args:
            name: Channel name
            
        Returns:
            True if channel exists and is enabled.
        """
        channel = self.channels.get(name)
        return channel is not None and channel.is_connected()
    
    def list_channels(self) -> List[str]:
        """List all configured channel names.
        
        Returns:
            List of channel names.
        """
        return list(self.channels.keys())
    
    def list_enabled_channels(self) -> List[str]:
        """List all enabled (connected) channels.
        
        Returns:
            List of enabled channel names.
        """
        return [name for name, ch in self.channels.items() if ch.is_connected()]
