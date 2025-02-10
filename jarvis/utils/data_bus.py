"""
Unified Data Bus for JARVIS
Provides centralized data integration and communication between components
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import pika
from pika.exceptions import AMQPConnectionError
import threading
from queue import Queue

class DataBusMessage:
    """Represents a message in the data bus"""
    def __init__(self,
                 source: str,
                 message_type: str,
                 payload: Any,
                 timestamp: Optional[datetime] = None):
        self.source = source
        self.message_type = message_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "source": self.source,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataBusMessage':
        """Create message from dictionary"""
        return cls(
            source=data["source"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class DataHub:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[DataBusMessage] = []
        self.max_history = 1000  # Maximum number of messages to keep
        
        # Setup message queue
        self._setup_message_queue()
        
        # Start message processing thread
        self.message_queue: Queue = Queue()
        self.processing_thread = threading.Thread(
            target=self._process_messages,
            daemon=True
        )
        self.processing_thread.start()
        
    def _setup_message_queue(self):
        """Setup RabbitMQ connection and channels"""
        try:
            # Connect to RabbitMQ
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange='jarvis',
                exchange_type='topic'
            )
            
            # Declare queue
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = result.method.queue
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange='jarvis',
                queue=self.queue_name,
                routing_key='#'
            )
            
            # Setup consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._message_callback,
                auto_ack=True
            )
            
            # Start consuming in separate thread
            threading.Thread(
                target=self.channel.start_consuming,
                daemon=True
            ).start()
            
        except AMQPConnectionError as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            
    def _message_callback(self,
                         ch: Any,
                         method: Any,
                         properties: Any,
                         body: bytes):
        """Callback for received messages"""
        try:
            message_dict = json.loads(body.decode())
            message = DataBusMessage.from_dict(message_dict)
            self.message_queue.put(message)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
    def _process_messages(self):
        """Process messages from queue"""
        while True:
            message = self.message_queue.get()
            self._handle_message(message)
            self.message_queue.task_done()
            
    def _handle_message(self, message: DataBusMessage):
        """Handle received message"""
        try:
            # Add to history
            self.message_history.append(message)
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)
                
            # Notify subscribers
            if message.message_type in self.subscribers:
                for callback in self.subscribers[message.message_type]:
                    try:
                        callback(message)
                    except Exception as e:
                        self.logger.error(
                            f"Error in subscriber callback: {e}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            
    async def publish(self,
                     source: str,
                     message_type: str,
                     payload: Any) -> bool:
        """
        Publish message to data bus
        
        Args:
            source: Source of the message
            message_type: Type of message
            payload: Message payload
            
        Returns:
            True if message was published successfully
        """
        try:
            message = DataBusMessage(source, message_type, payload)
            
            if self.channel:
                self.channel.basic_publish(
                    exchange='jarvis',
                    routing_key=message_type,
                    body=json.dumps(message.to_dict())
                )
            
            # Also process locally
            self.message_queue.put(message)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False
            
    def subscribe(self,
                 message_type: str,
                 callback: Callable[[DataBusMessage], None]) -> None:
        """
        Subscribe to messages of specific type
        
        Args:
            message_type: Type of messages to subscribe to
            callback: Callback function for messages
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(callback)
        
    def unsubscribe(self,
                    message_type: str,
                    callback: Callable[[DataBusMessage], None]) -> bool:
        """
        Unsubscribe from messages
        
        Args:
            message_type: Type of messages to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if unsubscribed successfully
        """
        try:
            if message_type in self.subscribers:
                self.subscribers[message_type].remove(callback)
                return True
            return False
        except ValueError:
            return False
            
    def get_message_history(self,
                          message_type: Optional[str] = None,
                          limit: Optional[int] = None) -> List[DataBusMessage]:
        """
        Get message history
        
        Args:
            message_type: Optional filter by message type
            limit: Optional limit on number of messages
            
        Returns:
            List of messages
        """
        messages = self.message_history
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        if limit:
            messages = messages[-limit:]
        return messages
        
    def clear_history(self) -> None:
        """Clear message history"""
        self.message_history = []
        
    def __del__(self):
        """Cleanup connections"""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")