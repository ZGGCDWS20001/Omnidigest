"""
Tests for Redis cache service.
Redis 缓存服务测试。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestCacheServiceInitialization:
    """
    Test cases for CacheService initialization.
    CacheService 初始化测试用例。
    """

    def test_cache_initialization_disabled(self):
        """
        Test CacheService initializes with caching disabled when redis_enabled is False.
        测试当 redis_enabled 为 False 时，CacheService 初始化为禁用状态。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            assert cache._enabled is False
            assert cache._client is None

    def test_cache_initialization_enabled(self):
        """
        Test CacheService initializes with caching enabled when redis_enabled is True.
        测试当 redis_enabled 为 True 时，CacheService 初始化为启用状态。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            assert cache._enabled is True


class TestCacheServiceGet:
    """
    Test cases for cache get operation.
    缓存获取操作测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService with enabled state."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    def test_get_returns_none_when_disabled(self):
        """
        Test get returns None when caching is disabled.
        测试当缓存禁用时，get 返回 None。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            result = cache.get("test_key")
            assert result is None

    @patch('omnidigest.core.cache.redis.Redis')
    def test_get_returns_cached_value(self, mock_redis_class, mock_cache):
        """
        Test get returns cached value when exists.
        测试当缓存值存在时，get 返回缓存值。
        """
        # Setup mock
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = json.dumps({"data": "test_value"})

        result = mock_cache.get("test_key")

        assert result == {"data": "test_value"}
        mock_redis.get.assert_called_once_with("test_key")

    @patch('omnidigest.core.cache.redis.Redis')
    def test_get_returns_none_when_key_not_found(self, mock_redis_class, mock_cache):
        """
        Test get returns None when key doesn't exist.
        测试当键不存在时，get 返回 None。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None

        result = mock_cache.get("nonexistent_key")

        assert result is None

    @patch('omnidigest.core.cache.redis.Redis')
    def test_get_handles_json_decode_error(self, mock_redis_class, mock_cache):
        """
        Test get handles JSON decode error gracefully.
        测试 get 优雅处理 JSON 解码错误。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = "invalid_json{"

        result = mock_cache.get("test_key")

        assert result is None


class TestCacheServiceSet:
    """
    Test cases for cache set operation.
    缓存设置操作测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    def test_set_returns_false_when_disabled(self):
        """
        Test set returns False when caching is disabled.
        测试当缓存禁用时，set 返回 False。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            result = cache.set("test_key", {"data": "value"})
            assert result is False

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_returns_true_on_success(self, mock_redis_class, mock_cache):
        """
        Test set returns True on successful cache write.
        测试成功写入缓存时，set 返回 True。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        result = mock_cache.set("test_key", {"data": "test_value"}, ttl=60)

        assert result is True
        mock_redis.setex.assert_called_once()

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_uses_correct_ttl(self, mock_redis_class, mock_cache):
        """
        Test set uses the specified TTL.
        测试 set 使用指定的 TTL。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        mock_cache.set("test_key", "value", ttl=300)

        # Verify setex was called with correct ttl
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 300  # ttl parameter

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_handles_redis_error(self, mock_redis_class, mock_cache):
        """
        Test set handles Redis errors gracefully.
        测试 set 优雅处理 Redis 错误。
        """
        import redis as redis_lib

        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.setex.side_effect = redis_lib.RedisError("Connection error")

        result = mock_cache.set("test_key", "value")

        assert result is False


class TestCacheServiceDelete:
    """
    Test cases for cache delete operation.
    缓存删除操作测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    def test_delete_returns_false_when_disabled(self):
        """
        Test delete returns False when caching is disabled.
        测试当缓存禁用时，delete 返回 False。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            result = cache.delete("test_key")
            assert result is False

    @patch('omnidigest.core.cache.redis.Redis')
    def test_delete_returns_true_on_success(self, mock_redis_class, mock_cache):
        """
        Test delete returns True on successful deletion.
        测试成功删除时，delete 返回 True。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        result = mock_cache.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")


class TestCacheServiceDeletePattern:
    """
    Test cases for cache delete pattern operation.
    缓存批量删除操作测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    def test_delete_pattern_returns_zero_when_disabled(self):
        """
        Test delete_pattern returns 0 when caching is disabled.
        测试当缓存禁用时，delete_pattern 返回 0。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            result = cache.delete_pattern("test:*")
            assert result == 0

    @patch('omnidigest.core.cache.redis.Redis')
    def test_delete_pattern_deletes_matching_keys(self, mock_redis_class, mock_cache):
        """
        Test delete_pattern deletes all matching keys.
        测试 delete_pattern 删除所有匹配的键。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.scan_iter.return_value = ["test:1", "test:2", "test:3"]

        result = mock_cache.delete_pattern("test:*")

        assert result == 3
        assert mock_redis.delete.call_count == 3


class TestCacheServiceExists:
    """
    Test cases for cache exists operation.
    缓存存在检查操作测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    def test_exists_returns_false_when_disabled(self):
        """
        Test exists returns False when caching is disabled.
        测试当缓存禁用时，exists 返回 False。
        """
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = False

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            result = cache.exists("test_key")
            assert result is False

    @patch('omnidigest.core.cache.redis.Redis')
    def test_exists_returns_true_when_key_exists(self, mock_redis_class, mock_cache):
        """
        Test exists returns True when key exists.
        测试当键存在时，exists 返回 True。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 1

        result = mock_cache.exists("test_key")

        assert result is True

    @patch('omnidigest.core.cache.redis.Redis')
    def test_exists_returns_false_when_key_not_exists(self, mock_redis_class, mock_cache):
        """
        Test exists returns False when key doesn't exist.
        测试当键不存在时，exists 返回 False。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 0

        result = mock_cache.exists("nonexistent_key")

        assert result is False


class TestCacheServiceConnection:
    """
    Test cases for Redis connection handling.
    Redis 连接处理测试用例。
    """

    @patch('omnidigest.core.cache.redis.Redis')
    def test_connection_failure_disables_cache(self, mock_redis_class):
        """
        Test connection failure disables caching.
        测试连接失败时禁用缓存。
        """
        import redis as redis_lib

        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            # Make ping raise connection error
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.side_effect = redis_lib.ConnectionError("Connection refused")

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            # Access client to trigger connection
            client = cache.client

            assert client is None
            assert cache._enabled is False

    @patch('omnidigest.core.cache.redis.Redis')
    def test_connection_timeout_handled(self, mock_redis_class):
        """
        Test connection timeout is handled gracefully.
        测试连接超时被优雅处理。
        """
        import redis as redis_lib

        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.side_effect = redis_lib.TimeoutError("Timeout")

            from omnidigest.core.cache import CacheService
            cache = CacheService()

            client = cache.client

            assert client is None
            assert cache._enabled is False


class TestCacheSerialization:
    """
    Test cases for cache value serialization.
    缓存值序列化测试用例。
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock CacheService."""
        with patch('omnidigest.core.cache.settings') as mock_settings:
            mock_settings.redis_enabled = True
            mock_settings.redis_host = 'localhost'
            mock_settings.redis_port = 6379
            mock_settings.redis_db = 0
            mock_settings.redis_password = ''

            from omnidigest.core.cache import CacheService
            return CacheService()

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_serializes_dict(self, mock_redis_class, mock_cache):
        """
        Test set serializes dictionary correctly.
        测试 set 正确序列化字典。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        test_data = {"name": "test", "value": 123, "nested": {"key": "val"}}
        mock_cache.set("test_key", test_data)

        # Verify the serialized data
        call_args = mock_redis.setex.call_args
        serialized = call_args[0][2]
        assert "name" in serialized
        assert "test" in serialized

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_serializes_list(self, mock_redis_class, mock_cache):
        """
        Test set serializes list correctly.
        测试 set 正确序列化列表。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        test_data = [1, 2, 3, "four", {"five": 5}]
        mock_cache.set("list_key", test_data)

        call_args = mock_redis.setex.call_args
        serialized = call_args[0][2]
        assert "1" in serialized

    @patch('omnidigest.core.cache.redis.Redis')
    def test_set_serializes_string(self, mock_redis_class, mock_cache):
        """
        Test set serializes string correctly.
        测试 set 正确序列化字符串。
        """
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        mock_cache.set("string_key", "Hello World")

        # Verify setex was called (strings are also JSON serialized)
        mock_redis.setex.assert_called_once()
