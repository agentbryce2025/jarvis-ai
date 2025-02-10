"""
Tests for JARVIS API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from jarvis.api import app

client = TestClient(app)

def test_status():
    """Test system status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_task_not_found():
    """Test getting non-existent task"""
    response = client.get("/tasks/invalid-task-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_chat_endpoint():
    """Test basic chat functionality"""
    request_data = {
        "message": "Hello, JARVIS",
        "context": {"type": "test"}
    }
    response = client.post("/chat", json=request_data)
    
    # Skip test when OpenAI API is not available
    if response.status_code == 500:
        error_msg = response.json().get("detail", "")
        if (
            "openai.AuthenticationError" in error_msg
            or "invalid_api_key" in error_msg
            or "Incorrect API key provided" in error_msg
        ):
            pytest.skip("Skipping test that requires OpenAI API")
            return
            
    assert response.status_code == 200
    assert "response" in response.json()
    assert "task_id" in response.json()