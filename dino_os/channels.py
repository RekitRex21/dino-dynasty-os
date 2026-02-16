"""
Channel plugins for Dino Dynasty OS.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent to path to import from channels/ folder
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from channels.telegram import TelegramChannel
from channels.discord import DiscordChannel
from channels.whatsapp import WhatsAppChannel

__all__ = ["TelegramChannel", "DiscordChannel", "WhatsAppChannel", "ChannelManager"]


class ChannelManager:
    """Manages all channel integrations."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.channels = {}
        
    def register(self, name, channel):
        self.channels[name] = channel
        
    async def send(self, channel_name: str, message: str) -> bool:
        """Send a message via the specified channel.
        
        Args:
            channel_name: Name of the channel to use
            message: Message content to send
            
        Returns:
            True if message was sent successfully
        """
        if channel_name in self.channels:
            channel = self.channels[channel_name]
            try:
                if hasattr(channel, 'send_message'):
                    await channel.send_message(message)
                    return True
                elif hasattr(channel, 'send'):
                    await channel.send(message)
                    return True
            except Exception as e:
                print(f"Error sending message via {channel_name}: {e}")
        return False
