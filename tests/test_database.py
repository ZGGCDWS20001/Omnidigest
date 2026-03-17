"""
Tests for database module.
数据库模块测试。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestDatabaseManager:
    """
    Test cases for DatabaseManager.
    DatabaseManager 测试用例。
    """

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_initialization(self, mock_pool):
        """
        Test DatabaseManager initialization.
        测试 DatabaseManager 初始化。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        assert db._pool is None

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_close_all(self, mock_pool):
        """
        Test close_all method closes the connection pool.
        测试 close_all 方法关闭连接池。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_pool_instance = Mock()
        db._pool = mock_pool_instance

        db.close_all()

        mock_pool_instance.closeall.assert_called_once()
        assert db._pool is None

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_get_connection_creates_pool_if_none(self, mock_pool):
        """
        Test that _get_connection creates a pool if none exists.
        测试 _get_connection 在没有连接池时创建一个。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_pool_instance = Mock()
        mock_conn = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance

        with db._get_connection() as conn:
            assert conn == mock_conn

        mock_pool.assert_called_once()

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    @patch('omnidigest.core.database.settings')
    def test_get_connection_uses_settings(self, mock_settings, mock_pool):
        """
        Test that connection pool uses correct settings.
        测试连接池使用正确的配置。
        """
        from omnidigest.core.database import DatabaseManager

        mock_settings.db_host = "testhost"
        mock_settings.db_port = 5432
        mock_settings.db_user = "testuser"
        mock_settings.db_password = "testpass"
        mock_settings.db_name = "testdb"

        db = DatabaseManager()
        mock_pool_instance = Mock()
        mock_conn = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance

        with db._get_connection() as conn:
            pass

        mock_pool.assert_called_once_with(
            minconn=1,
            maxconn=20,
            host="testhost",
            port=5432,
            user="testuser",
            password="testpass",
            dbname="testdb"
        )


class TestDatabaseManagerCheckIntegrity:
    """
    Test cases for check_integrity method.
    check_integrity 方法测试用例。
    """

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_check_integrity_all_tables_exist(self, mock_pool):
        """
        Test check_integrity returns True when all tables exist.
        测试所有表存在时 check_integrity 返回 True。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)  # Table exists
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance
        db._pool = mock_pool_instance

        result = db.check_integrity()

        assert result is True

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_check_integrity_missing_table(self, mock_pool):
        """
        Test check_integrity returns False when a table is missing.
        测试缺少表时 check_integrity 返回 False。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_conn = Mock()
        mock_cursor = Mock()
        # First call returns None (table doesn't exist)
        mock_cursor.fetchone.side_effect = [(1,), None, (1,), (1,), (1,), (1,)]
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance
        db._pool = mock_pool_instance

        result = db.check_integrity()

        assert result is False


class TestDatabaseManagerLLMMethods:
    """
    Test cases for LLM management methods.
    LLM 管理方法测试用例。
    """

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    @patch('omnidigest.core.database.RealDictCursor')
    def test_get_active_llm_models(self, mock_dict_cursor, mock_pool):
        """
        Test get_active_llm_models returns list of models.
        测试 get_active_llm_models 返回模型列表。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'name': 'model1', 'priority': 10},
            {'name': 'model2', 'priority': 5}
        ]
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance
        db._pool = mock_pool_instance

        result = db.get_active_llm_models()

        assert len(result) == 2
        assert result[0]['name'] == 'model1'

    @patch('omnidigest.core.database.ThreadedConnectionPool')
    def test_add_llm_model(self, mock_pool):
        """
        Test add_llm_model inserts a new model.
        测试 add_llm_model 插入新模型。
        """
        from omnidigest.core.database import DatabaseManager

        db = DatabaseManager()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        mock_pool_instance = Mock()
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance
        db._pool = mock_pool_instance

        result = db.add_llm_model(
            name="test_model",
            base_url="https://api.test.com",
            api_key="test_key",
            model_name="gpt-4",
            priority=10
        )

        assert result is not None
        mock_cursor.execute.assert_called_once()
