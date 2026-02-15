"""
Channel plugins for Dino Dynasty OS.
"""

import sys
from pathlib import Path

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
        
    def send(self, channel_name, message):
        if channel_name in self.channels:
            return self.channels[channel_name].send(message)
        return False
