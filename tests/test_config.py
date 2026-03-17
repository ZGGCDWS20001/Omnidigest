"""
Tests for configuration module.
配置模块测试。
"""
import pytest
from unittest.mock import patch, Mock


class TestSettings:
    """
    Test cases for Settings configuration.
    设置配置测试用例。
    """

    def test_settings_has_required_fields(self):
        """
        Test that Settings has all required configuration fields.
        测试 Settings 包含所有必需的配段。
        """
        from omnidigest.config import Settings

        # Test that Settings can be instantiated and has expected fields
        # We just check the loaded settings has expected attributes
        from omnidigest.config import settings

        # Database fields
        assert hasattr(settings, 'db_host')
        assert hasattr(settings, 'db_port')
        assert hasattr(settings, 'db_name')

        # LLM fields
        assert hasattr(settings, 'llm_api_key')
        assert hasattr(settings, 'llm_base_url')
        assert hasattr(settings, 'llm_model_name')

        # Breaking news fields
        assert hasattr(settings, 'enable_breaking_news')
        assert hasattr(settings, 'breaking_impact_threshold')
        assert hasattr(settings, 'breaking_push_dingtalk')

        # Twitter fields
        assert hasattr(settings, 'enable_twitter_alerts')
        assert hasattr(settings, 'twitter_push_telegram')

    def test_settings_is_singleton(self):
        """
        Test that settings is a singleton instance.
        测试 settings 是单例实例。
        """
        from omnidigest import config

        settings1 = config.settings
        settings2 = config.settings

        assert settings1 is settings2

    def test_environment_variable_override(self, monkeypatch):
        """
        Test that environment variables override defaults.
        测试环境变量覆盖默认值。
        """
        # Create a new Settings instance with custom env vars
        monkeypatch.setenv("DB_HOST", "testhost")
        monkeypatch.setenv("DB_PORT", "5433")
        monkeypatch.setenv("DB_NAME", "testdb")
        monkeypatch.setenv("LLM_MODEL_NAME", "gpt-4")

        # Need to reload module to pick up new env vars
        import importlib
        import omnidigest.config as config_module
        importlib.reload(config_module)

        settings = config_module.Settings()
        assert settings.db_host == "testhost"
        assert settings.db_port == 5433
        assert settings.db_name == "testdb"
        assert settings.llm_model_name == "gpt-4"

        # Restore original
        importlib.reload(config_module)


class TestDingRobotConfig:
    """
    Test cases for DingRobotConfig.
    钉钉机器人配置测试用例。
    """

    def test_default_values(self):
        """
        Test default DingRobotConfig values.
        测试默认 DingRobotConfig 值。
        """
        from omnidigest.config import DingRobotConfig

        config = DingRobotConfig(token="test_token")
        assert config.token == "test_token"
        assert config.secret == ""
        assert config.enable_daily is True
        assert config.enable_breaking is True
        assert config.enable_twitter is True

    def test_custom_values(self):
        """
        Test custom DingRobotConfig values.
        测试自定义 DingRobotConfig 值。
        """
        from omnidigest.config import DingRobotConfig

        config = DingRobotConfig(
            token="test_token",
            secret="test_secret",
            enable_daily=False,
            daily_template="custom.md.j2"
        )
        assert config.enable_daily is False
        assert config.daily_template == "custom.md.j2"


class TestTgRobotConfig:
    """
    Test cases for TgRobotConfig.
    Telegram 机器人配置测试用例。
    """

    def test_default_values(self):
        """
        Test default TgRobotConfig values.
        测试默认 TgRobotConfig 值。
        """
        from omnidigest.config import TgRobotConfig

        config = TgRobotConfig(chat_id="123456")
        assert config.chat_id == "123456"
        assert config.enable_daily is True
        assert config.enable_breaking is True
        assert config.enable_twitter is True

    def test_custom_values(self):
        """
        Test custom TgRobotConfig values.
        测试自定义 TgRobotConfig 值。
        """
        from omnidigest.config import TgRobotConfig

        config = TgRobotConfig(
            chat_id="123456",
            enable_breaking=False,
            breaking_template="custom.html.j2"
        )
        assert config.enable_breaking is False
        assert config.breaking_template == "custom.html.j2"
