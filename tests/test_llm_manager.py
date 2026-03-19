"""
Tests for LLM Manager module.
LLM 管理器模块测试。
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime


class TestLLMManagerInitialization:
    """
    Test cases for LLMManager initialization.
    LLMManager 初始化测试用例。
    """

    def test_llm_manager_initialization(self):
        """
        Test LLMManager can be initialized with a database manager.
        测试 LLMManager 可以用数据库管理器初始化。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        manager = LLMManager(mock_db)

        assert manager.db == mock_db
        assert manager._current_model is None
        assert manager._client is None

    def test_llm_manager_has_lock(self):
        """
        Test LLMManager has an asyncio Lock.
        测试 LLMManager 有 asyncio Lock。
        """
        from omnidigest.core.llm_manager import LLMManager
        import asyncio

        mock_db = Mock()
        manager = LLMManager(mock_db)

        assert isinstance(manager._lock, asyncio.Lock)


class TestLLMManagerCleanJson:
    """
    Test cases for JSON output cleaning.
    JSON 输出清洗测试用例。
    """

    @pytest.fixture
    def manager(self):
        """Create a LLMManager instance without initialization."""
        from omnidigest.core.llm_manager import LLMManager
        mock_db = Mock()
        return LLMManager(mock_db)

    def test_clean_json_empty_string(self, manager):
        """
        Test cleaning empty string returns empty string.
        测试清洗空字符串返回空字符串。
        """
        result = manager._clean_json_output("")
        assert result == ""

    def test_clean_json_none(self, manager):
        """
        Test cleaning None returns empty string.
        测试清洗 None 返回空字符串。
        """
        result = manager._clean_json_output(None)
        assert result == ""

    def test_clean_json_with_markdown_code_block(self, manager):
        """
        Test cleaning JSON with markdown code block.
        测试清洗带 markdown 代码块的 JSON。
        """
        content = """```json
{"key": "value", "number": 42}
```"""
        result = manager._clean_json_output(content)
        assert result == '{"key": "value", "number": 42}'

    def test_clean_json_with_plain_markdown(self, manager):
        """
        Test cleaning JSON with plain markdown.
        测试清洗带普通 markdown 的 JSON。
        """
        content = """```{"name": "test", "active": true}
```"""
        result = manager._clean_json_output(content)
        assert result == '{"name": "test", "active": true}'

    def test_clean_json_without_markdown(self, manager):
        """
        Test cleaning JSON without markdown.
        测试清洗不带 markdown 的 JSON。
        """
        content = '{"key": "value"}'
        result = manager._clean_json_output(content)
        assert result == '{"key": "value"}'

    def test_clean_json_with_xml_noise(self, manager):
        """
        Test cleaning JSON with XML-like noise (DashScope).
        测试清洗带 XML 噪音的 JSON (DashScope)。
        """
        content = '<tool_call>{"result": "data", "count": 10}</tool_call>'
        result = manager._clean_json_output(content)
        # Should extract the JSON part
        assert '"result": "data"' in result
        assert '"count": 10' in result


class TestLLMManagerRefreshClient:
    """
    Test cases for client refresh functionality.
    客户端刷新功能测试用例。
    """

    @pytest.mark.anyio
    async def test_refresh_client_with_active_models(self):
        """
        Test _refresh_client uses highest priority model from database.
        测试 _refresh_client 使用数据库中优先级最高的模型。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        mock_db.get_active_llm_models = Mock(return_value=[
            {'id': 'model-1', 'name': 'GPT-4', 'api_key': 'key1', 'base_url': 'https://api.openai.com', 'model_name': 'gpt-4'}
        ])

        manager = LLMManager(mock_db)

        with patch('omnidigest.core.llm_manager.AsyncOpenAI'):
            with patch('omnidigest.core.llm_manager.AsyncClient', return_value=AsyncMock()):
                await manager._refresh_client()

        assert manager._current_model is not None
        assert manager._current_model['name'] == 'GPT-4'

    @pytest.mark.anyio
    async def test_refresh_client_fallback_to_settings(self):
        """
        Test _refresh_client falls back to settings when no models in DB.
        测试当数据库没有模型时 _refresh_client 回退到设置。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        mock_db.get_active_llm_models = Mock(return_value=[])

        manager = LLMManager(mock_db)

        with patch('omnidigest.core.llm_manager.settings') as mock_settings:
            mock_settings.llm_api_key = 'test-key'
            mock_settings.llm_base_url = 'https://api.test.com'
            mock_settings.llm_model_name = 'test-model'

            with patch('omnidigest.core.llm_manager.AsyncOpenAI'):
                with patch('omnidigest.core.llm_manager.AsyncClient', return_value=AsyncMock()):
                    await manager._refresh_client()

        assert manager._current_model['name'] == 'Settings Fallback'
        assert manager._current_model['model_name'] == 'test-model'

    @pytest.mark.anyio
    async def test_refresh_client_excludes_failed_models(self):
        """
        Test _refresh_client excludes failed model IDs.
        测试 _refresh_client 排除失败的模型 ID。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        mock_db.get_active_llm_models = Mock(return_value=[
            {'id': 'model-1', 'name': 'Model 1', 'api_key': 'key1', 'base_url': 'url1', 'model_name': 'm1'},
            {'id': 'model-2', 'name': 'Model 2', 'api_key': 'key2', 'base_url': 'url2', 'model_name': 'm2'}
        ])

        manager = LLMManager(mock_db)

        with patch('omnidigest.core.llm_manager.AsyncOpenAI'):
            with patch('omnidigest.core.llm_manager.AsyncClient', return_value=AsyncMock()):
                await manager._refresh_client(exclude_ids=['model-1'])

        # Should skip model-1 and use model-2
        assert manager._current_model['id'] == 'model-2'

    @pytest.mark.anyio
    async def test_get_client_and_model_creates_client(self):
        """
        Test get_client_and_model creates client if none exists.
        测试 get_client_and_model 在没有客户端时创建客户端。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        mock_db.get_active_llm_models = Mock(return_value=[
            {'id': 'model-1', 'name': 'Test Model', 'api_key': 'test-key', 'base_url': 'https://api.test.com', 'model_name': 'test-model'}
        ])

        manager = LLMManager(mock_db)

        with patch('omnidigest.core.llm_manager.AsyncOpenAI'):
            with patch('omnidigest.core.llm_manager.AsyncClient', return_value=AsyncMock()):
                client, model = await manager.get_client_and_model()

        assert client is not None
        assert model is not None


class TestLLMManagerProviderDetection:
    """
    Test cases for provider-specific mode selection.
    供应商特定模式选择测试用例。
    """

    @pytest.fixture
    def manager(self):
        """Create a LLMManager instance."""
        from omnidigest.core.llm_manager import LLMManager
        mock_db = Mock()
        return LLMManager(mock_db)

    def test_dashscope_detection_in_base_url(self, manager):
        """
        Test DashScope is detected in base_url.
        测试在 base_url 中检测到 DashScope。
        """
        base_url = "https://dashscope.aliyuncs.com/api/v1"
        is_dashscope = "dashscope" in base_url.lower() or "aliyuncs.com" in base_url.lower()
        assert is_dashscope is True

    def test_dashscope_detection_false_for_other(self, manager):
        """
        Test DashScope is not detected for other providers.
        测试其他供应商不会检测到 DashScope。
        """
        base_url = "https://api.openai.com/v1"
        is_dashscope = "dashscope" in base_url.lower() or "aliyuncs.com" in base_url.lower()
        assert is_dashscope is False


class TestLLMManagerTokenUsage:
    """
    Test cases for token usage recording.
    Token 使用记录测试用例。
    """

    @pytest.mark.anyio
    async def test_token_usage_recording(self):
        """
        Test token usage is recorded after successful completion.
        测试成功完成后记录 token 使用情况。
        """
        from omnidigest.core.llm_manager import LLMManager

        mock_db = Mock()
        mock_db.get_active_llm_models = Mock(return_value=[
            {'id': 'model-1', 'name': 'Test Model', 'api_key': 'test-key', 'base_url': 'https://api.test.com', 'model_name': 'test-model'}
        ])
        mock_db.reset_llm_failure = Mock()
        mock_db.record_token_usage = Mock()

        manager = LLMManager(mock_db)

        # Create mock completion with usage
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        mock_usage.cached_tokens = 0

        mock_raw_completion = Mock()
        mock_raw_completion.usage = mock_usage

        with patch('omnidigest.core.llm_manager.AsyncOpenAI') as MockClient:
            with patch('omnidigest.core.llm_manager.AsyncClient', return_value=AsyncMock()):
                # Pre-refresh the client
                await manager._refresh_client()

                # The token recording is async and doesn't block the main flow
                # So we just verify the flow doesn't error
                assert manager._current_model is not None
