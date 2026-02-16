"""Computer Use Agent - Desktop automation and control for Dino Dynasty OS.

⚠️  WARNING: This agent can control your mouse and keyboard!
All actions are logged for safety and review.
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dino_os.agent_core import Agent

# Setup logging for safety
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"computer_use_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ComputerUseAgent')


class ComputerUseAgent(Agent):
    """Agent that can control the computer (mouse, keyboard, screenshots).
    
    ⚠️  All actions are logged for safety review.
    """
    
    name = "computer"
    description = "Controls mouse, keyboard, and takes screenshots"
    
    def __init__(self):
        super().__init__()
        self.action_history: List[Dict[str, Any]] = []
        self.screenshot_dir = Path(__file__).parent.parent / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Try to import GUI automation libraries
        self._pyautogui_available = False
        self._pillow_available = False
        self._init_gui_libs()
    
    def _init_gui_libs(self):
        """Initialize GUI automation libraries."""
        try:
            import pyautogui
            # Safety settings
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            pyautogui.PAUSE = 0.1  # Brief pause between actions
            self._pyautogui = pyautogui
            self._pyautogui_available = True
            logger.info("PyAutoGUI initialized successfully")
        except ImportError:
            logger.warning("PyAutoGUI not available. Install with: pip install pyautogui")
        
        try:
            from PIL import Image
            self._pillow_available = True
            logger.info("Pillow (PIL) available for screenshots")
        except ImportError:
            logger.warning("Pillow not available. Install with: pip install Pillow")
    
    def _log_action(self, action_type: str, details: Dict[str, Any]):
        """Log every action for safety review."""
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "details": details
        }
        self.action_history.append(action_record)
        logger.info(f"ACTION: {action_type} - {details}")
    
    async def run(self):
        """Run the computer use agent."""
        status = []
        
        if self._pyautogui_available:
            status.append("✅ Mouse/Keyboard control: Available")
        else:
            status.append("❌ Mouse/Keyboard control: Install pyautogui")
        
        if self._pillow_available:
            status.append("✅ Screenshots: Available")
        else:
            status.append("❌ Screenshots: Install Pillow")
        
        return {
            "status": "success",
            "output": "Computer Use Agent Ready\n\n" + "\n".join(status) + 
                     "\n\nAll actions are logged to: " + str(log_file)
        }
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot and save it.
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to saved screenshot
        """
        if not self._pyautogui_available:
            return "Error: pyautogui not installed"
        
        try:
            if filename is None:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.screenshot_dir / filename
            screenshot = self._pyautogui.screenshot()
            screenshot.save(filepath)
            
            self._log_action("screenshot", {"filepath": str(filepath)})
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return f"Error: {e}"
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        if not self._pyautogui_available:
            return False
        
        try:
            self._pyautogui.moveTo(x, y, duration=duration)
            self._log_action("mouse_move", {"x": x, "y": y, "duration": duration})
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False
    
    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, 
                   button: str = "left") -> bool:
        """Click mouse at position or current location.
        
        Args:
            x: Optional X coordinate (uses current if None)
            y: Optional Y coordinate (uses current if None)
            button: Mouse button (left, right, middle)
            
        Returns:
            True if successful
        """
        if not self._pyautogui_available:
            return False
        
        try:
            if x is not None and y is not None:
                self._pyautogui.click(x, y, button=button)
                self._log_action("mouse_click", {"x": x, "y": y, "button": button})
            else:
                self._pyautogui.click(button=button)
                self._log_action("mouse_click", {"button": button, "position": "current"})
            return True
        except Exception as e:
            logger.error(f"Mouse click failed: {e}")
            return False
    
    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Scroll the mouse wheel.
        
        Args:
            amount: Scroll amount (positive=up, negative=down)
            x: Optional X coordinate
            y: Optional Y coordinate
            
        Returns:
            True if successful
        """
        if not self._pyautogui_available:
            return False
        
        try:
            if x is not None and y is not None:
                self._pyautogui.scroll(amount, x, y)
            else:
                self._pyautogui.scroll(amount)
            
            self._log_action("scroll", {"amount": amount, "x": x, "y": y})
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.01) -> bool:
        """Type text using keyboard.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            True if successful
        """
        if not self._pyautogui_available:
            return False
        
        # Block potentially dangerous text
        dangerous_patterns = ['rm -rf', 'sudo', 'password', 'secret']
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                logger.warning(f"Blocked potentially dangerous text: {pattern}")
                return False
        
        try:
            self._pyautogui.typewrite(text, interval=interval)
            self._log_action("type_text", {"text": text[:50] + "..." if len(text) > 50 else text})
            return True
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key or key combination.
        
        Args:
            key: Key name (e.g., 'enter', 'ctrl', 'ctrl+c')
            
        Returns:
            True if successful
        """
        if not self._pyautogui_available:
            return False
        
        try:
            if '+' in key:
                # Hotkey combination
                keys = key.split('+')
                self._pyautogui.hotkey(*keys)
            else:
                self._pyautogui.press(key)
            
            self._log_action("press_key", {"key": key})
            return True
        except Exception as e:
            logger.error(f"Press key failed: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions.
        
        Returns:
            (width, height) tuple
        """
        if not self._pyautogui_available:
            return (0, 0)
        
        return self._pyautogui.size()
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            (x, y) tuple
        """
        if not self._pyautogui_available:
            return (0, 0)
        
        return self._pyautogui.position()
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get history of all actions performed."""
        return self.action_history
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute a high-level task (basic implementation).
        
        Args:
            task_description: Natural language description of task
            
        Returns:
            Result dictionary
        """
        logger.info(f"Executing task: {task_description}")
        
        # Simple task parsing (expand this with LLM integration)
        task_lower = task_description.lower()
        
        if "screenshot" in task_lower or "capture" in task_lower:
            result = self.take_screenshot()
            return {"status": "success", "output": f"Screenshot saved: {result}"}
        
        elif "click" in task_lower:
            self.click_mouse()
            return {"status": "success", "output": "Mouse clicked"}
        
        elif "type" in task_lower or "write" in task_lower:
            # Extract text after "type" or "write"
            text = task_description.split("type")[-1].split("write")[-1].strip()
            if text:
                success = self.type_text(text)
                return {"status": "success" if success else "error", 
                       "output": f"Typed: {text}" if success else "Failed to type"}
        
        return {"status": "success", "output": f"Task logged: {task_description}"}
