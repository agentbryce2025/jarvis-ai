"""
Personality System for JARVIS
Manages personality traits and adapts behavior based on interaction history
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

class PersonaEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_persona = config["default"]
        self.interaction_history = []
        self.logger = logging.getLogger(__name__)
        
    def get_current_persona(self) -> Dict[str, Any]:
        """Return the current active persona"""
        return self.current_persona
        
    def adapt_persona(self, context: Dict[str, Any]) -> None:
        """
        Adapt personality based on interaction context
        
        Args:
            context: Dictionary containing interaction context
        """
        try:
            # Analyze context and adjust personality parameters
            self._update_personality_parameters(context)
            self._record_interaction(context)
        except Exception as e:
            self.logger.error(f"Failed to adapt persona: {e}")
            self._revert_to_default()
            
    def _update_personality_parameters(self, context: Dict[str, Any]) -> None:
        """
        Update personality parameters based on context
        
        Args:
            context: Interaction context
        """
        try:
            # Adjust formality based on context
            if "formality" in context:
                if context["formality"] == "high":
                    self.current_persona["formality"] = min(1.0, self.current_persona["formality"] + 0.1)
                elif context["formality"] == "low":
                    self.current_persona["formality"] = max(0.0, self.current_persona["formality"] - 0.1)
                    
            # Adjust humor based on user emotion
            if "user_emotion" in context:
                if context["user_emotion"] == "happy":
                    self.current_persona["humor"] = min(1.0, self.current_persona["humor"] + 0.1)
                elif context["user_emotion"] == "sad":
                    self.current_persona["humor"] = max(0.0, self.current_persona["humor"] - 0.1)
                    
            # Adjust empathy based on interaction
            if "interaction_history" in context:
                positive_interactions = sum(1 for x in context["interaction_history"] if x == "positive")
                if positive_interactions > len(context["interaction_history"]) / 2:
                    self.current_persona["empathy"] = min(1.0, self.current_persona["empathy"] + 0.1)
                    
        except Exception as e:
            self.logger.error(f"Failed to update personality parameters: {e}")
            self._revert_to_default()
        
    def _record_interaction(self, context: Dict[str, Any]) -> None:
        """
        Record interaction for future reference
        
        Args:
            context: Interaction context
        """
        interaction = {
            "timestamp": datetime.now(),
            "context": context,
            "persona_state": self.current_persona.copy()
        }
        self.interaction_history.append(interaction)
        
    def _revert_to_default(self) -> None:
        """Revert to default personality settings"""
        self.current_persona = self.config["default"]
        self.logger.info("Reverted to default personality")
        
    def get_response_style(self) -> Dict[str, float]:
        """
        Get current response style parameters
        
        Returns:
            Dictionary of style parameters
        """
        return {
            "formality": self.current_persona["formality"],
            "humor": self.current_persona["humor"],
            "empathy": self.current_persona["empathy"]
        }
        
    def analyze_relationship(self) -> Dict[str, Any]:
        """
        Analyze relationship status based on interaction history
        
        Returns:
            Dictionary containing relationship metrics
        """
        # Implement relationship analysis
        return {
            "rapport_level": 0.0,
            "trust_level": 0.0,
            "interaction_quality": 0.0
        }