"""
Pytest configuration and shared fixtures.
Pytest 配置和共享 fixtures。
"""
import os
import sys
import pytest
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def clean_env():
    """
    Clean environment variables before each test.
    每个测试前清理环境变量。
    """
    # Store original env
    original_env = os.environ.copy()

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_settings():
    """
    Fixture providing mocked settings.
    提供模拟设置的 fixture。
    """
    from unittest.mock import Mock

    settings = Mock()
    settings.db_host = "localhost"
    settings.db_port = 5432
    settings.db_user = "testuser"
    settings.db_password = "testpass"
    settings.db_name = "testdb"
    settings.llm_api_key = "test_key"
    settings.llm_base_url = "https://api.test.com"
    settings.llm_model_name = "test-model"
    settings.enable_breaking_news = True
    settings.breaking_impact_threshold = 80
    settings.enable_twitter_alerts = True

    return settings


@pytest.fixture
def sample_article():
    """
    Fixture providing a sample article dictionary.
    提供示例文章字典的 fixture。
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Article Title",
        "content": "Test article content for testing purposes.",
        "source_url": "https://example.com/test-article",
        "source_name": "Test Source",
        "status": 0,
        "category": "tech",
        "score": 85,
        "publish_time": "2024-01-01 12:00:00"
    }


@pytest.fixture
def sample_rss_source():
    """
    Fixture providing a sample RSS source dictionary.
    提供示例 RSS 源字典的 fixture。
    """
    return {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "url": "https://example.com/rss",
        "name": "Test RSS Feed",
        "enabled": True,
        "fail_count": 0
    }
