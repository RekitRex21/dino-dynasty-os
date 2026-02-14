"""Message Bus - Inter-agent communication for Dino Dynasty OS."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Message:
    """Represents a message on the bus."""
    id: str
    topic: str
    payload: Dict[str, Any]
    sender: str
    priority: MessagePriority
    timestamp: str
    reply_to: Optional[str] = None
    correlation_id: Optional[str] = None


class MessageBus:
    """Pub/sub message bus for inter-agent communication."""
    
    def __init__(self):
        """Initialize the message bus."""
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._history: List[Message] = []
        self._max_history = 1000

    async def start(self) -> None:
        """Start the message bus."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._process_messages())

    async def stop(self) -> None:
        """Stop the message bus."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to a topic.
        
        Args:
            topic: Topic pattern (supports wildcards like "agent.*")
            callback: Async callback function
        """
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """Unsubscribe from a topic.
        
        Args:
            topic: Topic pattern
            callback: Callback to remove
            
        Returns:
            True if removed.
        """
        if topic in self._subscriptions:
            try:
                self._subscriptions[topic].remove(callback)
                return True
            except ValueError:
                pass
        return False

    async def publish(self, topic: str, payload: Dict[str, Any], sender: str,
                      priority: MessagePriority = MessagePriority.NORMAL,
                      reply_to: Optional[str] = None,
                      correlation_id: Optional[str] = None) -> str:
        """Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            payload: Message payload
            sender: Sender identifier
            priority: Message priority
            reply_to: Optional topic to reply to
            correlation_id: Optional correlation ID
            
        Returns:
            Message ID.
        """
        message = Message(
            id=str(uuid4()),
            topic=topic,
            payload=payload,
            sender=sender,
            priority=priority,
            timestamp=datetime.utcnow().isoformat(),
            reply_to=reply_to,
            correlation_id=correlation_id
        )
        
        await self._message_queue.put(message)
        return message.id

    async def send_direct(self, recipient: str, payload: Dict[str, Any], sender: str) -> str:
        """Send a direct message to an agent.
        
        Args:
            recipient: Recipient agent name
            payload: Message payload
            sender: Sender identifier
            
        Returns:
            Message ID.
        """
        return await self.publish(f"direct.{recipient}", payload, sender)

    async def request(self, topic: str, payload: Dict[str, Any], sender: str,
                      timeout: float = 5.0) -> Optional[Message]:
        """Send a request and wait for response.
        
        Args:
            topic: Request topic
            payload: Request payload
            sender: Sender identifier
            timeout: Response timeout
            
        Returns:
            Response message or None.
        """
        correlation_id = str(uuid4())
        await self.publish(topic, payload, sender, correlation_id=correlation_id)
        
        # Wait for response (simplified - in real implementation, use a future/complete)
        future = asyncio.get_event_loop().create_future()
        
        def response_handler(msg: Message):
            if msg.correlation_id == correlation_id:
                future.set_result(msg)
        
        self.subscribe(f"response.{correlation_id}", response_handler)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self.unsubscribe(f"response.{correlation_id}", response_handler)

    async def _process_messages(self) -> None:
        """Process messages from the queue."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0
                )
                await self._dispatch(message)
                
                # Add to history
                self._history.append(message)
                if len(self._history) > self._max_history:
                    self._history.pop(0)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Message bus error: {e}")

    async def _dispatch(self, message: Message) -> None:
        """Dispatch a message to all matching subscribers."""
        # Check exact matches first
        callbacks = []
        
        # Exact match
        if message.topic in self._subscriptions:
            callbacks.extend(self._subscriptions[message.topic])
        
        # Wildcard matches
        topic_parts = message.topic.split('.')
        for pattern, subs in self._subscriptions.items():
            if '*' in pattern or '#' in pattern:
                pattern_parts = pattern.split('.')
                if self._match_pattern(topic_parts, pattern_parts):
                    callbacks.extend(subs)
        
        # Execute callbacks
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                print(f"Message callback error: {e}")

    def _match_pattern(self, topic_parts: List[str], pattern_parts: List[str]) -> bool:
        """Match a topic against a pattern with wildcards.
        
        Args:
            topic_parts: Topic split into parts
            pattern_parts: Pattern split into parts
            
        Returns:
            True if matches.
        """
        if len(topic_parts) != len(pattern_parts):
            return False
        
        for topic_part, pattern_part in zip(topic_parts, pattern_parts):
            if pattern_part == '#':
                return True
            if pattern_part != '*' and pattern_part != topic_part:
                return False
        
        return True

    def get_history(self, topic: Optional[str] = None, limit: int = 100) -> List[Message]:
        """Get message history.
        
        Args:
            topic: Optional topic filter
            limit: Maximum messages to return
            
        Returns:
            List of messages.
        """
        messages = self._history
        if topic:
            messages = [m for m in messages if m.topic == topic]
        return messages[-limit:]
