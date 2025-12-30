import pytest
import asyncio
from echidna_agent.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_url():
    return settings.ECHIDNA_AGENT_DB_URL
