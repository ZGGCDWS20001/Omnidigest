"""
Tests for Twitter event aggregation and deduplication.
推特事件聚合与去重测试。
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestTwitterAlerter:
    """
    Test cases for TwitterAlerter.
    TwitterAlerter 测试用例。
    """

    def test_push_alert(self):
        """
        Test push_alert sends event notification.
        测试 push_alert 发送事件通知。
        """
        from omnidigest.domains.twitter.alerter import TwitterAlerter

        with patch('omnidigest.domains.twitter.alerter.NotificationService') as MockNotifier:
            mock_notifier = MockNotifier.return_value
            alerter = TwitterAlerter(notifier=mock_notifier)

            event_data = {
                'id': 'event-1',
                'event_title': 'Test Event',
                'summary': 'Test summary',
                'category': 'Politics',
                'source_count': 2,
                'sources': [
                    {'author_screen_name': 'user1'},
                    {'author_screen_name': 'user2'}
                ],
                'first_tweet_id': '123',
                'push_count': 1
            }

            with patch('omnidigest.domains.twitter.alerter.settings') as mock_settings:
                mock_settings.twitter_push_telegram = True
                mock_settings.twitter_push_dingtalk = True
                alerter.push_alert(event_data)

                # Should send to both Telegram and DingTalk
                mock_notifier.push_to_telegram.assert_called_once()
                mock_notifier.push_to_dingtalk.assert_called_once()

                # Check event_type is "twitter"
                call_args = mock_notifier.push_to_telegram.call_args
                assert call_args[1]['event_type'] == 'twitter'

    def test_push_alert_telegram_only(self):
        """
        Test push_alert only sends to telegram when configured.
        测试只配置 Telegram 时只发送到 Telegram。
        """
        from omnidigest.domains.twitter.alerter import TwitterAlerter

        with patch('omnidigest.domains.twitter.alerter.NotificationService') as MockNotifier:
            mock_notifier = MockNotifier.return_value
            alerter = TwitterAlerter(notifier=mock_notifier)

            event_data = {
                'id': 'event-1',
                'event_title': 'Test Event',
                'summary': 'Test summary',
                'category': 'Politics',
                'source_count': 1,
                'sources': [{'author_screen_name': 'user1'}],
                'first_tweet_id': '123',
                'push_count': 1
            }

            with patch('omnidigest.domains.twitter.alerter.settings') as mock_settings:
                mock_settings.twitter_push_telegram = True
                mock_settings.twitter_push_dingtalk = False
                alerter.push_alert(event_data)

                mock_notifier.push_to_telegram.assert_called_once()
                mock_notifier.push_to_dingtalk.assert_not_called()


class TestTwitterProcessorEventClustering:
    """
    Test cases for TwitterProcessor event clustering.
    推特处理器事件聚类测试用例。
    使用同步包装模拟异步调用
    """

    def test_handle_event_for_tweet_new_event_above_threshold(self):
        """
        Test _handle_event_for_tweet returns event when threshold is 1.
        测试阈值为1时新事件返回事件数据。
        """
        import asyncio
        from omnidigest.domains.twitter.processor import TwitterProcessor

        # Setup mocks
        mock_db = Mock()
        mock_db.find_similar_twitter_events.return_value = []  # No similar events
        mock_db.create_twitter_event.return_value = 'new-event-id'
        mock_db.link_tweet_to_event.return_value = True
        mock_db.get_twitter_event_by_id.return_value = {
            'id': 'new-event-id',
            'event_title': 'Test Event',
            'source_count': 1,
            'summary': 'Test summary',
            'category': 'Politics'
        }
        mock_db.get_twitter_event_tweet_sources.return_value = [
            {'author_screen_name': 'user1'}
        ]

        mock_llm = Mock()
        mock_alerter = Mock()

        processor = TwitterProcessor(mock_db, mock_llm, mock_alerter)

        stream = {
            'tweet_id': '123',
            'author_screen_name': 'user1',
            'raw_text': 'Breaking news about something important'
        }
        result = Mock()
        result.summary_zh = 'Test summary'
        result.category = 'Politics'
        result.impact_score = 85

        with patch('omnidigest.domains.twitter.processor.settings') as mock_settings:
            mock_settings.enable_twitter_alerts = True
            mock_settings.twitter_event_lookback_minutes = 10
            mock_settings.twitter_event_push_threshold = 1  # Threshold is 1

            # Run async test in sync context
            async def run_test():
                return await processor._handle_event_for_tweet(stream, result)

            event = asyncio.run(run_test())

            # New event should be created
            mock_db.create_twitter_event.assert_called_once()
            # When threshold=1, event should be returned for immediate push
            assert event is not None
            assert event['id'] == 'new-event-id'

    def test_handle_event_for_tweet_new_event_below_threshold(self):
        """
        Test _handle_event_for_tweet returns None for new event when threshold > 1.
        测试阈值为2时新事件返回None（因为只有1个来源）。
        """
        import asyncio
        from omnidigest.domains.twitter.processor import TwitterProcessor

        # Setup mocks
        mock_db = Mock()
        mock_db.find_similar_twitter_events.return_value = []  # No similar events
        mock_db.create_twitter_event.return_value = 'new-event-id'
        mock_db.link_tweet_to_event.return_value = True
        mock_db.get_twitter_event_by_id.return_value = {
            'id': 'new-event-id',
            'event_title': 'Test Event',
            'source_count': 1,
            'summary': 'Test summary',
            'category': 'Politics'
        }
        mock_db.get_twitter_event_tweet_sources.return_value = [
            {'author_screen_name': 'user1'}
        ]

        mock_llm = Mock()
        mock_alerter = Mock()

        processor = TwitterProcessor(mock_db, mock_llm, mock_alerter)

        stream = {
            'tweet_id': '123',
            'author_screen_name': 'user1',
            'raw_text': 'Breaking news about something important'
        }
        result = Mock()
        result.summary_zh = 'Test summary'
        result.category = 'Politics'
        result.impact_score = 85

        with patch('omnidigest.domains.twitter.processor.settings') as mock_settings:
            mock_settings.enable_twitter_alerts = True
            mock_settings.twitter_event_lookback_minutes = 10
            mock_settings.twitter_event_push_threshold = 2  # Threshold is 2

            # Run async test in sync context
            async def run_test():
                return await processor._handle_event_for_tweet(stream, result)

            event = asyncio.run(run_test())

            # New event should be created but not returned (source_count=1 < threshold=2)
            mock_db.create_twitter_event.assert_called_once()
            assert event is None

    def test_handle_event_for_tweet_existing_event(self):
        """
        Test _handle_event_for_tweet links to existing event.
        测试 _handle_event_for_tweet 链接到现有事件。
        """
        import asyncio
        from omnidigest.domains.twitter.processor import TwitterProcessor

        # Setup mocks
        mock_db = Mock()
        mock_db.find_similar_twitter_events.return_value = [
            {'id': 'existing-event', 'source_count': 1}
        ]
        mock_db.increment_twitter_event_source_count.return_value = 2
        mock_db.link_tweet_to_event.return_value = True
        mock_db.update_twitter_event.return_value = True
        mock_db.get_twitter_event_by_id.return_value = {
            'id': 'existing-event',
            'event_title': 'Existing Event',
            'source_count': 2,
            'summary': 'Existing summary',
            'category': 'Politics'
        }
        mock_db.get_twitter_event_tweet_sources.return_value = [
            {'author_screen_name': 'user1'},
            {'author_screen_name': 'user2'}
        ]

        mock_llm = Mock()
        mock_alerter = Mock()

        processor = TwitterProcessor(mock_db, mock_llm, mock_alerter)

        stream = {
            'tweet_id': '456',
            'author_screen_name': 'user2',
            'raw_text': 'More news about the same topic'
        }
        result = Mock()
        result.summary_zh = 'More details'
        result.category = 'Politics'
        result.impact_score = 80

        with patch('omnidigest.domains.twitter.processor.settings') as mock_settings:
            mock_settings.enable_twitter_alerts = True
            mock_settings.twitter_event_lookback_minutes = 10
            mock_settings.twitter_event_push_threshold = 2

            async def run_test():
                return await processor._handle_event_for_tweet(stream, result)

            event = asyncio.run(run_test())

            # Should link to existing event and increment count
            mock_db.link_tweet_to_event.assert_called_once()
            mock_db.increment_twitter_event_source_count.assert_called_once()
            assert event is not None
            assert event['source_count'] == 2

    def test_handle_event_for_tweet_no_alerts_when_disabled(self):
        """
        Test _handle_event_for_tweet returns None when alerts disabled.
        测试禁用提醒时返回 None。
        """
        import asyncio
        from omnidigest.domains.twitter.processor import TwitterProcessor

        mock_db = Mock()
        mock_llm = Mock()
        mock_alerter = Mock()

        processor = TwitterProcessor(mock_db, mock_llm, mock_alerter)

        stream = {'tweet_id': '123'}
        result = Mock()
        result.summary_zh = 'Test'
        result.category = 'Politics'
        result.impact_score = 85

        with patch('omnidigest.domains.twitter.processor.settings') as mock_settings:
            mock_settings.enable_twitter_alerts = False

            async def run_test():
                return await processor._handle_event_for_tweet(stream, result)

            event = asyncio.run(run_test())

            # Should return None without creating any events
            mock_db.create_twitter_event.assert_not_called()
            assert event is None

    def test_handle_event_below_threshold_no_alert(self):
        """
        Test no alert when source_count below threshold.
        测试来源数低于阈值时不发送提醒。
        """
        import asyncio
        from omnidigest.domains.twitter.processor import TwitterProcessor

        mock_db = Mock()
        mock_db.find_similar_twitter_events.return_value = []  # No similar events
        mock_db.create_twitter_event.return_value = 'new-event-id'
        mock_db.link_tweet_to_event.return_value = True
        mock_db.get_twitter_event_by_id.return_value = {
            'id': 'new-event-id',
            'event_title': 'Test Event',
            'source_count': 1,  # Only 1 source
            'summary': 'Test summary',
            'category': 'Politics'
        }
        mock_db.get_twitter_event_tweet_sources.return_value = [
            {'author_screen_name': 'user1'}
        ]

        mock_llm = Mock()
        mock_alerter = Mock()

        processor = TwitterProcessor(mock_db, mock_llm, mock_alerter)

        stream = {
            'tweet_id': '123',
            'author_screen_name': 'user1',
            'raw_text': 'Breaking news'
        }
        result = Mock()
        result.summary_zh = 'Test summary'
        result.category = 'Politics'
        result.impact_score = 85

        with patch('omnidigest.domains.twitter.processor.settings') as mock_settings:
            mock_settings.enable_twitter_alerts = True
            mock_settings.twitter_event_lookback_minutes = 10
            mock_settings.twitter_event_push_threshold = 2  # Threshold is 2

            async def run_test():
                return await processor._handle_event_for_tweet(stream, result)

            event = asyncio.run(run_test())

            # Event created but no alert because source_count (1) < threshold (2)
            mock_db.create_twitter_event.assert_called_once()
            assert event is None  # No alert should be pushed


class TestTwitterEventConfig:
    """
    Test cases for Twitter event configuration.
    推特事件配置测试用例。
    """

    def test_default_config_values(self):
        """
        Test default configuration values.
        测试默认配置值。
        """
        from omnidigest.config import settings

        assert settings.twitter_event_lookback_minutes == 10
        assert settings.twitter_event_push_threshold == 2

    def test_config_from_env(self, monkeypatch):
        """
        Test configuration from environment variables.
        测试从环境变量读取配置。
        """
        monkeypatch.setenv("TWITTER_EVENT_LOOKBACK_MINUTES", "30")
        monkeypatch.setenv("TWITTER_EVENT_PUSH_THRESHOLD", "5")

        # Reload config module to pick up env vars
        import importlib
        import omnidigest.config
        importlib.reload(omnidigest.config)

        from omnidigest.config import settings as fresh_settings

        assert fresh_settings.twitter_event_lookback_minutes == 30
        assert fresh_settings.twitter_event_push_threshold == 5


class TestNotificationPusher:
    """
    Test cases for notification pusher Twitter event type support.
    通知推送器 Twitter 事件类型支持测试。
    """

    def test_pusher_twitter_dingtalk(self):
        """
        Test pusher handles twitter event type for DingTalk.
        测试推送器处理 DingTalk 的 twitter 事件类型。
        """
        from omnidigest.notifications.pusher import NotificationService

        with patch('omnidigest.notifications.pusher.settings') as mock_settings:
            mock_robot = Mock()
            mock_robot.token = "test_token"
            mock_robot.secret = ""
            mock_robot.enable_twitter = True
            mock_robot.twitter_template = "test_template"
            mock_settings.ding_robots = [mock_robot]
            mock_settings.tg_robots = []

            with patch.object(NotificationService, 'render_template', return_value="content"):
                with patch.object(NotificationService, '_send_one_dingtalk') as mock_send:
                    pusher = NotificationService()
                    pusher.push_to_dingtalk("title", {"event": "data"}, event_type="twitter")

                    mock_send.assert_called_once()

    def test_pusher_twitter_telegram(self):
        """
        Test pusher handles twitter event type for Telegram.
        测试推送器处理 Telegram 的 twitter 事件类型。
        """
        from omnidigest.notifications.pusher import NotificationService

        with patch('omnidigest.notifications.pusher.settings') as mock_settings:
            mock_robot = Mock()
            mock_robot.chat_id = "123456"
            mock_robot.enable_twitter = True
            mock_robot.twitter_template = "test_template"
            mock_settings.tg_robots = [mock_robot]
            mock_settings.ding_robots = []

            with patch.object(NotificationService, 'render_template', return_value="content"):
                with patch.object(NotificationService, 'send_telegram') as mock_send:
                    pusher = NotificationService()
                    pusher.push_to_telegram({"event": "data"}, event_type="twitter")

                    mock_send.assert_called_once()
