import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List


# -- Mock LLM Provider --

class MockLLMResponse:
    """Simulates an LLM response for SQL generation."""
    def __init__(self, sql: str = "SELECT revenue FROM financial_results WHERE quarter = 'Q3' AND year = 2024"):
        self.sql = sql


@pytest.fixture
def mock_llm():
    """Return a mock that returns a predetermined SQL query. Prevents LLM API calls in unit tests."""
    llm = MagicMock()
    llm.generate_sql.return_value = MockLLMResponse()
    return llm


# -- Mock Pinecone --

class MockPineconeMatch:
    """Simulates a Pinecone query match."""
    def __init__(self, score: float = 0.92, metadata: Dict[str, Any] | None = None):
        self.score = score
        self.metadata = metadata or {"source": "internal_kb", "text": "The company expanded into Europe in 2024"}


class MockPineconeResponse:
    """Simulates a Pinecone query response."""
    def __init__(self, matches: List[MockPineconeMatch] | None = None):
        self.matches = matches or [MockPineconeMatch()]


@pytest.fixture
def mock_pinecone():
    """Return a mock that returns predetermined similarity scores."""
    pc = MagicMock()
    pc.query.return_value = MockPineconeResponse()
    return pc


# -- Mock DB Session --

@pytest.fixture
def mock_db_session():
    """Returns a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.close = AsyncMock()
    return session


# -- Celery Eager Mode --

@pytest.fixture
def celery_eager():
    """Configure Celery to run tasks synchronously for integration tests."""
    with patch.dict("os.environ", {
        "CELERY_TASK_ALWAYS_EAGER": "true",
        "CELERY_TASK_EAGER_PROPAGATES": "true",
    }):
        yield
