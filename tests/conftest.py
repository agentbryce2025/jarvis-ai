"""
Test configuration for JARVIS
"""

import pytest
import yaml
from pathlib import Path

pytest_plugins = ["pytest_asyncio"]

def pytest_addoption(parser):
    parser.addini(
        "asyncio_default_fixture_loop_scope",
        "specify the default scope for asyncio fixtures",
        default="function"
    )

@pytest.fixture(scope="session")
def test_config():
    config_path = Path(__file__).parent.parent / "jarvis" / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="function")
def memory_config(test_config):
    return {
        "short_term": {
            "type": "redis",
            "ttl": 1800,
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "mid_term": {
            "type": "chromadb",
            "collection": "recent_interactions",
            "retention_days": 30
        },
        "long_term": {
            "type": "postgresql",
            "table": "historical_memory",
            "connection_string": "sqlite:///jarvis_memory.db"
        }
    }

@pytest.fixture(scope="function")
def task_config(test_config):
    return test_config["task_planning"]

@pytest.fixture(scope="function")
def system_config(test_config):
    return test_config["security"]

@pytest.fixture(scope="function")
def persona_config(test_config):
    return test_config["personality"]