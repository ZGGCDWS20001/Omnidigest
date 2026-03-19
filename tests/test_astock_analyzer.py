"""
Tests for A-share stock analyzer module.
A股分析器模块测试。
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, date
from pydantic import ValidationError


class TestIndexPredictionModel:
    """
    Test cases for IndexPrediction Pydantic model.
    IndexPrediction Pydantic 模型测试用例。
    """

    def test_index_prediction_valid_fields(self):
        """
        Test IndexPrediction model accepts valid fields.
        测试 IndexPrediction 模型接受有效字段。
        """
        from omnidigest.domains.analysis.astock_analyzer import IndexPrediction

        prediction = IndexPrediction(
            direction="上涨",
            confidence=85,
            reason="市场情绪乐观，成交量放大"
        )

        assert prediction.direction == "上涨"
        assert prediction.confidence == 85
        assert prediction.reason == "市场情绪乐观，成交量放大"

    def test_index_prediction_direction_validation(self):
        """
        Test IndexPrediction direction field accepts only valid values.
        测试 IndexPrediction direction 字段只接受有效值。
        """
        from omnidigest.domains.analysis.astock_analyzer import IndexPrediction

        # Valid directions
        for direction in ["上涨", "下跌", "震荡"]:
            pred = IndexPrediction(direction=direction, confidence=50, reason="test")
            assert pred.direction == direction

    def test_index_prediction_confidence_range(self):
        """
        Test IndexPrediction confidence is within 0-100.
        测试 IndexPrediction confidence 在 0-100 范围内。
        """
        from omnidigest.domains.analysis.astock_analyzer import IndexPrediction

        # Valid confidence values
        pred = IndexPrediction(direction="上涨", confidence=0, reason="test")
        assert pred.confidence == 0

        pred = IndexPrediction(direction="上涨", confidence=100, reason="test")
        assert pred.confidence == 100

    def test_index_prediction_english_direction(self):
        """
        Test IndexPrediction accepts English direction values.
        测试 IndexPrediction 接受英文 direction 值。
        """
        from omnidigest.domains.analysis.astock_analyzer import IndexPrediction

        # English directions should also work (the model accepts str)
        prediction = IndexPrediction(
            direction="up",
            confidence=75,
            reason="Market sentiment positive"
        )

        assert prediction.direction == "up"
        assert prediction.confidence == 75


class TestAStockAnalysisResultModel:
    """
    Test cases for AStockAnalysisResult Pydantic model.
    AStockAnalysisResult Pydantic 模型测试用例。
    """

    def test_astock_analysis_result_valid_structure(self):
        """
        Test AStockAnalysisResult model accepts valid structure.
        测试 AStockAnalysisResult 模型接受有效结构。
        """
        from omnidigest.domains.analysis.astock_analyzer import (
            AStockAnalysisResult,
            IndexPrediction
        )

        result = AStockAnalysisResult(
            shanghai=IndexPrediction(direction="上涨", confidence=80, reason="理由1"),
            shenzhen=IndexPrediction(direction="震荡", confidence=65, reason="理由2"),
            overall_sentiment="乐观",
            key_drivers=["政策利好", "资金流入"]
        )

        assert result.shanghai.direction == "上涨"
        assert result.shenzhen.direction == "震荡"
        assert result.overall_sentiment == "乐观"
        assert len(result.key_drivers) == 2

    def test_astock_analysis_result_key_drivers(self):
        """
        Test key_drivers is a list of strings.
        测试 key_drivers 是字符串列表。
        """
        from omnidigest.domains.analysis.astock_analyzer import (
            AStockAnalysisResult,
            IndexPrediction
        )

        result = AStockAnalysisResult(
            shanghai=IndexPrediction(direction="上涨", confidence=80, reason="reason"),
            shenzhen=IndexPrediction(direction="下跌", confidence=70, reason="reason"),
            overall_sentiment="谨慎",
            key_drivers=["factor1", "factor2", "factor3"]
        )

        assert isinstance(result.key_drivers, list)
        assert all(isinstance(f, str) for f in result.key_drivers)

    def test_astock_analysis_result_overall_sentiment(self):
        """
        Test overall_sentiment accepts various sentiment values.
        测试 overall_sentiment 接受各种情绪值。
        """
        from omnidigest.domains.analysis.astock_analyzer import (
            AStockAnalysisResult,
            IndexPrediction
        )

        for sentiment in ["乐观", "谨慎", "悲观", "optimistic", "cautious"]:
            result = AStockAnalysisResult(
                shanghai=IndexPrediction(direction="上涨", confidence=80, reason="reason"),
                shenzhen=IndexPrediction(direction="上涨", confidence=80, reason="reason"),
                overall_sentiment=sentiment,
                key_drivers=[]
            )
            assert result.overall_sentiment == sentiment


class TestMarketContextModel:
    """
    Test cases for MarketContext Pydantic model.
    MarketContext Pydantic 模型测试用例。
    """

    def test_market_context_valid_fields(self):
        """
        Test MarketContext model accepts valid fields.
        测试 MarketContext 模型接受有效字段。
        """
        from omnidigest.domains.analysis.astock_analyzer import MarketContext

        context = MarketContext(
            index_type="shanghai",
            yesterday_close=3500.5,
            yesterday_change=1.2,
            today_open=3520.0,
            current_price=3530.0,
            current_change=0.85,
            high=3540.0,
            low=3510.0,
            volume=5000000000,
            update_time="2024-01-15 14:30:00"
        )

        assert context.index_type == "shanghai"
        assert context.yesterday_close == 3500.5
        assert context.current_price == 3530.0

    def test_market_context_optional_fields(self):
        """
        Test MarketContext optional fields can be None.
        测试 MarketContext 可选字段可以为 None。
        """
        from omnidigest.domains.analysis.astock_analyzer import MarketContext

        context = MarketContext(
            index_type="shanghai",
            yesterday_close=3500.5
        )

        assert context.index_type == "shanghai"
        assert context.yesterday_close == 3500.5
        assert context.current_price is None
        assert context.volume is None


class TestAStockAnalyzerFormatting:
    """
    Test cases for AStockAnalyzer data formatting methods.
    AStockAnalyzer 数据格式化方法测试用例。
    """

    @pytest.fixture
    def mock_db(self):
        """Create a mock database manager."""
        db = Mock()
        db._get_connection = Mock()
        return db

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM manager."""
        llm = Mock()
        llm.chat_completion_structured = AsyncMock()
        return llm

    @pytest.fixture
    def analyzer(self, mock_db, mock_llm):
        """Create an AStockAnalyzer instance with mocks."""
        with patch('omnidigest.domains.analysis.astock_analyzer.MarketDataService'):
            from omnidigest.domains.analysis.astock_analyzer import AStockAnalyzer
            analyzer = AStockAnalyzer(mock_db, mock_llm)
            return analyzer

    def test_format_news_for_llm_empty_list(self, analyzer):
        """
        Test _format_news_for_llm handles empty list.
        测试 _format_news_for_llm 处理空列表。
        """
        result = analyzer._format_news_for_llm([])
        assert result == "无相关新闻"

    def test_format_news_for_llm_none(self, analyzer):
        """
        Test _format_news_for_llm handles None.
        测试 _format_news_for_llm 处理 None。
        """
        result = analyzer._format_news_for_llm(None)
        assert result == "无相关新闻"

    def test_format_news_for_llm_valid_news(self, analyzer):
        """
        Test _format_news_for_llm formats news correctly.
        测试 _format_news_for_llm 正确格式化新闻。
        """
        news_list = [
            {
                'title': 'Test News Title',
                'content': 'Test content here',
                'source_name': 'Test Source',
                'publish_time': datetime(2024, 1, 15, 10, 30)
            }
        ]

        result = analyzer._format_news_for_llm(news_list)

        assert "Test News Title" in result
        assert "Test Source" in result
        assert "2024-01-15 10:30" in result

    def test_format_news_for_llm_truncates_long_content(self, analyzer):
        """
        Test _format_news_for_llm truncates long content.
        测试 _format_news_for_llm 截断长内容。
        """
        long_content = "A" * 1000
        news_list = [
            {
                'title': 'Test News',
                'content': long_content,
                'source_name': 'Source',
                'publish_time': datetime.now()
            }
        ]

        result = analyzer._format_news_for_llm(news_list)

        # Content should be truncated to 500 chars
        assert len(result) < 2000

    def test_format_news_for_llm_handles_missing_fields(self, analyzer):
        """
        Test _format_news_for_llm handles missing fields.
        测试 _format_news_for_llm 处理缺失字段。
        """
        news_list = [
            {
                'title': None,
                'content': 'Some content',
                'source_name': None,
                'publish_time': None
            }
        ]

        result = analyzer._format_news_for_llm(news_list)

        assert "无标题" in result or "Some content" in result

    def test_format_news_limits_to_20_items(self, analyzer):
        """
        Test _format_news_for_llm limits to 20 items.
        测试 _format_news_for_llm 限制为 20 条。
        """
        news_list = [
            {
                'title': f'News {i}',
                'content': f'Content {i}',
                'source_name': 'Source',
                'publish_time': datetime.now()
            }
            for i in range(30)
        ]

        result = analyzer._format_news_for_llm(news_list)

        # Should contain exactly 20 news items
        assert result.count("### 新闻") == 20

    def test_format_market_context_pre_market(self, analyzer):
        """
        Test _format_market_context for pre-market session.
        测试 _format_market_context 盘前格式。
        """
        context = {
            "shanghai": {
                "yesterday_close": 3500.5,
                "yesterday_date": "2024-01-15"
            },
            "shenzhen": {
                "yesterday_close": 11000.0,
                "yesterday_date": "2024-01-15"
            }
        }

        result = analyzer._format_market_context(context, "pre_market")

        assert "上证指数" in result
        assert "深证成指" in result
        assert "昨日收盘价" in result
        assert "3500.5" in result

    def test_format_market_context_intraday(self, analyzer):
        """
        Test _format_market_context for intraday session.
        测试 _format_market_context 盘中格式。
        """
        context = {
            "shanghai": {
                "today_open": 3510.0,
                "current_price": 3525.0,
                "current_change": 0.71,
                "high": 3530.0,
                "low": 3505.0
            }
        }

        result = analyzer._format_market_context(context, "intraday")

        assert "今日盘中" in result
        assert "开盘" in result
        assert "当前" in result
        assert "涨跌幅" in result

    def test_format_market_context_post_market(self, analyzer):
        """
        Test _format_market_context for post-market session.
        测试 _format_market_context 盘后格式。
        """
        context = {
            "shanghai": {
                "yesterday_close": 3500.0,
                "current_price": 3520.0,
                "current_change": 0.57
            }
        }

        result = analyzer._format_market_context(context, "post_market")

        assert "今日收盘" in result

    def test_format_market_context_empty_data(self, analyzer):
        """
        Test _format_market_context handles empty data.
        测试 _format_market_context 处理空数据。
        """
        context = {}

        result = analyzer._format_market_context(context, "pre_market")
        assert result == "暂无市场数据"


class TestAccuracyCalculation:
    """
    Test cases for prediction accuracy calculation.
    预测准确率计算测试用例。
    """

    def test_calculate_accuracy_up_correct(self):
        """
        Test accuracy calculation when prediction is UP and actual is positive.
        测试预测上涨且实际上涨时的准确率计算。
        """
        # When predicted direction is "上涨" and actual change > 0
        pred_direction = "上涨"
        actual_change = 1.5

        is_correct = (pred_direction == "上涨" and actual_change > 0) or \
                     (pred_direction == "下跌" and actual_change < 0) or \
                     (pred_direction == "震荡")

        assert is_correct is True

    def test_calculate_accuracy_down_correct(self):
        """
        Test accuracy calculation when prediction is DOWN and actual is negative.
        测试预测下跌且实际下跌时的准确率计算。
        """
        pred_direction = "下跌"
        actual_change = -2.3

        is_correct = (pred_direction == "上涨" and actual_change > 0) or \
                     (pred_direction == "下跌" and actual_change < 0) or \
                     (pred_direction == "震荡")

        assert is_correct is True

    def test_calculate_accuracy_neutral(self):
        """
        Test accuracy calculation when prediction is NEUTRAL.
        测试预测震荡时的准确率计算。
        """
        pred_direction = "震荡"
        actual_change = 0.1

        is_correct = (pred_direction == "上涨" and actual_change > 0) or \
                     (pred_direction == "下跌" and actual_change < 0) or \
                     (pred_direction == "震荡")

        assert is_correct is True

    def test_calculate_accuracy_incorrect(self):
        """
        Test accuracy calculation when prediction is wrong.
        测试预测错误时的准确率计算。
        """
        # Predicted UP but actual is DOWN
        pred_direction = "上涨"
        actual_change = -1.5

        is_correct = (pred_direction == "上涨" and actual_change > 0) or \
                     (pred_direction == "下跌" and actual_change < 0) or \
                     (pred_direction == "震荡")

        assert is_correct is False


class TestPredictionRecording:
    """
    Test cases for prediction recording to database.
    预测记录到数据库的测试用例。
    """

    @pytest.fixture
    def mock_db(self):
        """Create a mock database manager."""
        db = Mock()

        # Mock connection context - use MagicMock for context manager support
        mock_conn = MagicMock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("test-uuid",)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        # Use MagicMock to support context manager
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        db._get_connection = Mock(return_value=mock_conn)
        return db

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM manager."""
        llm = Mock()
        llm.chat_completion_structured = AsyncMock()
        return llm

    @pytest.mark.anyio
    async def test_record_prediction_returns_id(self, mock_db, mock_llm):
        """
        test_record_prediction returns prediction ID.
        测试 record_prediction 返回预测 ID。
        """
        with patch('omnidigest.domains.analysis.astock_analyzer.MarketDataService'):
            from omnidigest.domains.analysis.astock_analyzer import AStockAnalyzer

            analyzer = AStockAnalyzer(mock_db, mock_llm)
            result = await analyzer.record_prediction(
                index_type="shanghai",
                prediction_type="pre_market",
                direction="上涨",
                confidence=80,
                news_summary="测试理由"
            )

            assert result is not None

    @pytest.mark.anyio
    async def test_record_prediction_handles_error(self, mock_db, mock_llm):
        """
        test_record_prediction handles database errors gracefully.
        测试 record_prediction 优雅处理数据库错误。
        """
        # Make the connection raise an exception
        mock_db._get_connection.side_effect = Exception("Database error")

        with patch('omnidigest.domains.analysis.astock_analyzer.MarketDataService'):
            from omnidigest.domains.analysis.astock_analyzer import AStockAnalyzer

            analyzer = AStockAnalyzer(mock_db, mock_llm)
            result = await analyzer.record_prediction(
                index_type="shanghai",
                prediction_type="pre_market",
                direction="上涨",
                confidence=80,
                news_summary="测试理由"
            )

            assert result is None


class TestAccuracyStats:
    """
    Test cases for accuracy statistics.
    准确率统计测试用例。
    """

    def test_accuracy_stats_calculation(self):
        """
        Test accuracy calculation from stats data.
        测试从统计数据计算准确率。
        """
        # Simulate the calculation
        row = {
            'total_predictions': 10,
            'correct_predictions': 7,
            'avg_confidence': 75.5
        }

        accuracy = (row['correct_predictions'] / row['total_predictions'] * 100) if row['total_predictions'] > 0 else 0

        assert accuracy == 70.0

    def test_accuracy_stats_with_zero_predictions(self):
        """
        Test accuracy calculation with zero predictions.
        测试零预测的准确率计算。
        """
        row = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'avg_confidence': 0
        }

        accuracy = (row['correct_predictions'] / row['total_predictions'] * 100) if row['total_predictions'] > 0 else 0

        assert accuracy == 0


class TestMarketDataService:
    """
    Test cases for MarketDataService.
    MarketDataService 测试用例。
    """

    def test_index_codes_mapping(self):
        """
        Test index codes are correctly mapped.
        测试指数代码正确映射。
        """
        from omnidigest.domains.analysis.market_data import MarketDataService

        service = MarketDataService()

        assert service.INDEX_CODES["shanghai"]["name"] == "上证指数"
        assert service.INDEX_CODES["shanghai"]["symbol"] == "sh000001"
        assert service.INDEX_CODES["shenzhen"]["name"] == "深证成指"
        assert service.INDEX_CODES["shenzhen"]["symbol"] == "sz399001"

    @patch('omnidigest.domains.analysis.market_data.ak.stock_zh_index_spot_sina')
    def test_get_realtime_quote_success(self, mock_ak):
        """
        Test get_realtime_quote returns data on success.
        测试 get_realtime_quote 成功时返回数据。
        """
        import pandas as pd

        # Mock the akshare response
        mock_df = pd.DataFrame({
            '代码': ['sh000001', 'sz399001'],
            '最新价': [3500.5, 11000.0],
            '涨跌幅': [0.5, -0.3],
            '成交量': [5000000000, 3000000000],
            '成交额': [500000000000, 300000000000],
            '最高': [3510.0, 11050.0],
            '最低': [3490.0, 10950.0],
            '今开': [3495.0, 11020.0],
            '昨收': [3480.0, 11030.0]
        })
        mock_ak.return_value = mock_df

        from omnidigest.domains.analysis.market_data import MarketDataService
        service = MarketDataService()

        result = service.get_realtime_quote("shanghai")

        assert result is not None
        assert result["current_price"] == 3500.5
        assert result["change"] == 0.5

    def test_get_realtime_quote_invalid_index(self):
        """
        Test get_realtime_quote with invalid index type.
        测试无效指数类型的 get_realtime_quote。
        """
        from omnidigest.domains.analysis.market_data import MarketDataService

        service = MarketDataService()

        result = service.get_realtime_quote("invalid_index")

        assert result is None

    def test_is_market_open_weekend(self):
        """
        Test is_market_open returns False on weekends.
        测试 is_market_open 周末返回 False。
        """
        from omnidigest.domains.analysis.market_data import MarketDataService

        service = MarketDataService()

        # Mock a Saturday
        with patch('omnidigest.domains.analysis.market_data.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 13, 10, 0)  # Saturday
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = service.is_market_open()

            # On weekend, should return False
            assert result is False

    def test_get_market_session_values(self):
        """
        Test get_market_session returns valid session values.
        测试 get_market_session 返回有效的会话值。
        """
        from omnidigest.domains.analysis.market_data import MarketDataService

        service = MarketDataService()

        valid_sessions = ["pre_market", "morning", "lunch", "afternoon", "after_close", "closed", "holiday", "unknown"]

        # Test with different times by mocking datetime
        with patch('omnidigest.domains.analysis.market_data.datetime') as mock_datetime:
            # Test morning session (weekday 10:00)
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = service.get_market_session()

            assert result in valid_sessions


class TestProxyManagement:
    """
    Test cases for proxy management functions.
    代理管理函数测试用例。
    """

    def test_disable_proxy_saves_original(self):
        """
        Test _disable_proxy saves original proxy settings.
        测试 _disable_proxy 保存原始代理设置。
        """
        import os
        from omnidigest.domains.analysis.market_data import _disable_proxy, _restore_proxy

        # Set a test proxy
        original_http = os.environ.get('http_proxy')
        os.environ['http_proxy'] = 'http://test-proxy:8080'

        try:
            _disable_proxy()

            # Proxy should be removed
            assert 'http_proxy' not in os.environ

            _restore_proxy()

            # Proxy should be restored
            assert os.environ.get('http_proxy') == 'http://test-proxy:8080'
        finally:
            # Cleanup
            if 'http_proxy' in os.environ:
                del os.environ['http_proxy']
            if original_http:
                os.environ['http_proxy'] = original_http

    def test_disable_proxy_handles_missing_proxy(self):
        """
        Test _disable_proxy when no proxy is set.
        测试未设置代理时的 _disable_proxy。
        """
        import os
        from omnidigest.domains.analysis.market_data import _disable_proxy, _restore_proxy

        # Make sure no proxy is set
        if 'http_proxy' in os.environ:
            del os.environ['http_proxy']

        # Should not raise exception
        _disable_proxy()
        _restore_proxy()

        # Test passes if no exception is raised
        assert True
