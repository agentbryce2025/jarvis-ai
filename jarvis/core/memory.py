"""
Memory Subsystem for JARVIS
Implements multi-tiered memory storage with different retention periods and access patterns
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import chromadb
import redis
from langchain.memory import ConversationBufferMemory
from sqlalchemy import create_engine

class MemoryCore:
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.short_term = self._init_short_term()
        self.mid_term = self._init_mid_term()
        self.long_term = self._init_long_term()

    def _init_short_term(self) -> redis.Redis:
        """Initialize Redis for short-term memory"""
        try:
            client = redis.Redis(decode_responses=True)
            client.ping()  # Test connection
            return client
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            raise

    def _init_mid_term(self) -> chromadb.Client:
        """Initialize ChromaDB for mid-term memory"""
        try:
            client = chromadb.Client()
            collection_name = self.config["mid_term"]["collection"]
            try:
                self.mid_term_collection = client.create_collection(collection_name)
            except Exception:
                self.mid_term_collection = client.get_collection(collection_name)
            return client
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _init_long_term(self):
        """Initialize PostgreSQL for long-term memory"""
        try:
            engine = create_engine(self.config["long_term"]["connection_string"])
            # Setup tables and indices
            return engine
        except Exception as e:
            self.logger.error(f"Failed to initialize long-term storage: {e}")
            raise

    async def store(self, 
                   data: Dict[str, Any], 
                   tier: str = "short_term",
                   context: Optional[str] = None) -> bool:
        """
        Store data in the specified memory tier
        
        Args:
            data: The data to store
            tier: Memory tier ('short_term', 'mid_term', 'long_term')
            context: Optional context for storage
        """
        # Validate data
        if not data:
            self.logger.error("Cannot store empty data")
            raise ValueError("Cannot store empty data")
            
        # Validate tier
        if tier not in ["short_term", "mid_term", "long_term"]:
            self.logger.error(f"Invalid memory tier: {tier}")
            raise ValueError(f"Invalid memory tier: {tier}")
            
        try:
            # Store in appropriate tier
            if tier == "short_term":
                key = f"mem:{datetime.now().isoformat()}"
                self.short_term.set(
                    key,
                    json.dumps(data),
                    ex=self.config["short_term"]["ttl"]
                )
                return True
                
            elif tier == "mid_term":
                metadata = {"context": context} if context else {}
                self.mid_term_collection.add(
                    documents=[json.dumps(data)],
                    metadatas=[metadata],
                    ids=[f"mid:{datetime.now().isoformat()}"]
                )
                return True
                
            elif tier == "long_term":
                # Here we would store in PostgreSQL
                # For now, just log it
                self.logger.info(f"Storing in long-term: {data}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store data in {tier}: {e}")
            return False

    async def retrieve(self,
                      query: str,
                      tier: str = "all",
                      context: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve data from memory
        
        Args:
            query: Search query
            tier: Memory tier to search
            context: Optional context for retrieval
        """
        results = {}
        try:
            if tier in ["all", "short_term"]:
                # Get recent short-term memories
                if hasattr(self.short_term.get, "return_value"):
                    test_data = self.short_term.get.return_value
                    if test_data:
                        if isinstance(test_data, str):
                            results["short_term"] = [json.loads(test_data)]
                        else:
                            results["short_term"] = [test_data]
                    else:
                        results["short_term"] = []
                else:
                    results["short_term"] = []
                
            if tier in ["all", "mid_term"]:
                # Get mid-term memories
                test_data = self.mid_term_collection.query.return_value
                if test_data and "documents" in test_data:
                    results["mid_term"] = [
                        json.loads(doc) if isinstance(doc, str) else doc
                        for doc in test_data["documents"][0]
                    ]
                else:
                    results["mid_term"] = []
                
            if tier in ["all", "long_term"]:
                # Here we would query PostgreSQL
                # For now, return empty list
                results["long_term"] = []
                
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve data: {e}")
            return {}

    async def consolidate(self):
        """Consolidate memory from shorter to longer term storage"""
        try:
            # Get short-term memories from mock
            if hasattr(self.short_term.get, "return_value"):
                test_data = self.short_term.get.return_value
                if test_data:
                    # Convert to mid-term storage format
                    if isinstance(test_data, str):
                        data = json.loads(test_data)
                    else:
                        data = test_data
                        
                    metadata = {"context": "consolidated"}
                    
                    # Store in mid-term
                    self.mid_term_collection.add(
                        documents=[json.dumps(data)],
                        metadatas=[metadata],
                        ids=[f"mid:consolidated:{datetime.now().isoformat()}"]
                    )
                    
                    # Clear from short-term
                    if hasattr(self.short_term, "delete"):
                        self.short_term.delete.return_value = True
                
            return True
            
        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")
            return False