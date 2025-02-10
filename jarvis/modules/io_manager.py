"""
Multimodal Input/Output Manager for JARVIS
Handles different types of inputs and outputs including text, voice, and potentially images
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import asyncio
import json
from datetime import datetime

import whisper
from gtts import gTTS
import torch
from transformers import pipeline

class InputOutputManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_models()
        self.active_conversations: Dict[str, List[Dict[str, Any]]] = {}
        
    def _initialize_models(self):
        """Initialize required models for I/O processing"""
        try:
            # Initialize speech-to-text
            self.stt_model = whisper.load_model("base")
            
            # Initialize image processing if enabled
            if self.config.get("image", {}).get("enabled", False):
                self.image_processor = pipeline("image-to-text")
                
            self.logger.info("I/O models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize I/O models: {e}")
            raise
            
    async def process_input(self, 
                          input_data: Union[str, bytes, Path],
                          input_type: str = "text",
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data of various types
        
        Args:
            input_data: Input to process
            input_type: Type of input ('text', 'voice', 'image')
            context: Optional processing context
            
        Returns:
            Dictionary containing processed input
        """
        try:
            if input_type == "text":
                return await self._process_text_input(input_data)
            elif input_type == "voice":
                return await self._process_voice_input(input_data)
            elif input_type == "image":
                return await self._process_image_input(input_data)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to process {input_type} input: {e}")
            return {"status": "error", "error": str(e)}
            
    async def generate_output(self,
                            content: str,
                            output_type: str = "text",
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate output in specified format
        
        Args:
            content: Content to output
            output_type: Type of output ('text', 'voice')
            options: Optional output options
            
        Returns:
            Dictionary containing output data
        """
        try:
            if output_type == "text":
                return await self._generate_text_output(content, options)
            elif output_type == "voice":
                return await self._generate_voice_output(content, options)
            else:
                raise ValueError(f"Unsupported output type: {output_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate {output_type} output: {e}")
            return {"status": "error", "error": str(e)}
            
    async def _process_text_input(self, 
                                text: str) -> Dict[str, Any]:
        """Process text input"""
        return {
            "status": "success",
            "type": "text",
            "content": text,
            "timestamp": datetime.now()
        }
        
    async def _process_voice_input(self, 
                                 audio_data: Union[bytes, Path]) -> Dict[str, Any]:
        """Process voice input using Whisper"""
        try:
            # Convert audio to text
            result = self.stt_model.transcribe(str(audio_data))
            
            return {
                "status": "success",
                "type": "voice",
                "content": result["text"],
                "confidence": result.get("confidence", 0.0),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Voice processing failed: {e}")
            
    async def _process_image_input(self, 
                                 image_data: Union[bytes, Path]) -> Dict[str, Any]:
        """Process image input"""
        if not self.config["image"]["enabled"]:
            raise ValueError("Image processing is not enabled")
            
        try:
            # Process image
            result = self.image_processor(str(image_data))
            
            return {
                "status": "success",
                "type": "image",
                "content": result,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Image processing failed: {e}")
            
    async def _generate_text_output(self,
                                  content: str,
                                  options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate text output"""
        return {
            "status": "success",
            "type": "text",
            "content": content,
            "timestamp": datetime.now()
        }
        
    async def _generate_voice_output(self,
                                   content: str,
                                   options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate voice output using gTTS"""
        try:
            options = options or {}
            lang = options.get("language", "en")
            
            # Generate speech
            tts = gTTS(text=content, lang=lang)
            output_file = Path("/tmp/output.mp3")
            tts.save(str(output_file))
            
            return {
                "status": "success",
                "type": "voice",
                "content": str(output_file),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Voice generation failed: {e}")
            
    def start_conversation(self) -> str:
        """
        Start a new conversation
        
        Returns:
            Conversation ID
        """
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_conversations[conversation_id] = []
        return conversation_id
        
    def add_to_conversation(self,
                          conversation_id: str,
                          message: Dict[str, Any]) -> None:
        """
        Add message to conversation history
        
        Args:
            conversation_id: ID of the conversation
            message: Message to add
        """
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        self.active_conversations[conversation_id].append({
            **message,
            "timestamp": datetime.now()
        })
        
    def get_conversation_history(self,
                               conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of conversation messages
        """
        if conversation_id not in self.active_conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        return self.active_conversations[conversation_id]