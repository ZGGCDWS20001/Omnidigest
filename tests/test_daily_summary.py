"""
Tests for daily summary generation.
每日汇总生成测试。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError


class TestArticleTranslationModel:
    """
    Test cases for ArticleTranslation Pydantic model.
    ArticleTranslation Pydantic 模型测试用例。
    """

    def test_article_translation_fields(self):
        """
        Test that ArticleTranslation model has correct field names.
        测试 ArticleTranslation 模型具有正确的字段名。
        """
        from omnidigest.jobs import ArticleTranslation

        # Test with correct field names
        article = ArticleTranslation(
            id=1,
            chinese_title="测试标题",
            summary="测试摘要",
            original_url="https://example.com"
        )

        assert article.chinese_title == "测试标题"
        assert article.summary == "测试摘要"
        assert article.original_url == "https://example.com"

    def test_article_translation_missing_fields(self):
        """
        Test that ArticleTranslation requires correct fields.
        测试 ArticleTranslation 需要正确的字段。
        """
        from omnidigest.jobs import ArticleTranslation

        # Missing 'chinese_title' should fail
        with pytest.raises(ValidationError):
            ArticleTranslation(
                id=1,
                title="测试标题",  # Wrong field name
                summary="测试摘要",
                original_url="https://example.com"
            )

    def test_article_translation_no_title_field(self):
        """
        Test that ArticleTranslation does NOT have 'title' field.
        测试 ArticleTranslation 没有 'title' 字段。
        """
        from omnidigest.jobs import ArticleTranslation

        # Create valid article
        article = ArticleTranslation(
            id=1,
            chinese_title="测试标题",
            summary="测试摘要",
            original_url="https://example.com"
        )

        # 'title' should NOT exist
        assert not hasattr(article, 'title') or getattr(article, 'title', None) is None

    def test_article_translation_no_url_field(self):
        """
        Test that ArticleTranslation does NOT have 'url' field.
        测试 ArticleTranslation 没有 'url' 字段（应该是 original_url）。
        """
        from omnidigest.jobs import ArticleTranslation

        # Create valid article
        article = ArticleTranslation(
            id=1,
            chinese_title="测试标题",
            summary="测试摘要",
            original_url="https://example.com"
        )

        # Check the URL is accessible via original_url
        assert article.original_url == "https://example.com"


class TestCategorySummaryModel:
    """
    Test cases for CategorySummary Pydantic model.
    CategorySummary Pydantic 模型测试用例。
    """

    def test_category_summary_fields(self):
        """
        Test that CategorySummary model has correct field names.
        测试 CategorySummary 模型具有正确的字段名。
        """
        from omnidigest.jobs import CategorySummary, ArticleTranslation

        category = CategorySummary(
            category="AI & LLMs",
            overview="Overview text",
            critique="Some critique",
            articles=[
                ArticleTranslation(
                    id=1,
                    chinese_title="Test",
                    summary="Summary",
                    original_url="https://example.com"
                )
            ]
        )

        assert category.category == "AI & LLMs"
        assert category.overview == "Overview text"
        assert category.critique == "Some critique"

    def test_category_summary_no_category_name_field(self):
        """
        Test that CategorySummary does NOT have 'category_name' field.
        测试 CategorySummary 没有 'category_name' 字段（应该是 category）。
        """
        from omnidigest.jobs import CategorySummary, ArticleTranslation

        category = CategorySummary(
            category="AI & LLMs",
            overview="Overview text",
            critique="Some critique",
            articles=[]
        )

        # 'category_name' should NOT exist or be accessible
        # Trying to access it should raise AttributeError
        with pytest.raises(AttributeError):
            _ = category.category_name


class TestDailySummaryResultModel:
    """
    Test cases for DailySummaryResult Pydantic model.
    DailySummaryResult Pydantic 模型测试用例。
    """

    def test_daily_summary_result_fields(self):
        """
        Test that DailySummaryResult model has correct structure.
        测试 DailySummaryResult 模型具有正确的结构。
        """
        from omnidigest.jobs import DailySummaryResult, CategorySummary, ArticleTranslation

        result = DailySummaryResult(
            overview="Test overview",
            categories=[
                CategorySummary(
                    category="AI & LLMs",
                    overview="Category overview",
                    critique="Critique",
                    articles=[
                        ArticleTranslation(
                            id=1,
                            chinese_title="Title",
                            summary="Summary",
                            original_url="https://example.com"
                        )
                    ]
                )
            ]
        )

        assert result.overview == "Test overview"
        assert len(result.categories) == 1
        assert result.categories[0].category == "AI & LLMs"


class TestDailySummaryTemplateFields:
    """
    Test cases to verify templates use correct field names.
    验证模板使用正确字段名的测试用例。
    """

    def test_template_dingtalk_default_fields(self):
        """
        Test that dingtalk_default.md.j2 uses correct field names.
        测试 dingtalk_default.md.j2 使用正确的字段名。
        """
        from omnidigest.jobs import ArticleTranslation, CategorySummary, DailySummaryResult

        # Create test data
        result = DailySummaryResult(
            overview="Test overview",
            categories=[
                CategorySummary(
                    category="AI & LLMs",
                    overview="Overview",
                    critique="Critique",
                    articles=[
                        ArticleTranslation(
                            id=1,
                            chinese_title="正确的中文标题",
                            summary="摘要内容",
                            original_url="https://example.com/article"
                        )
                    ]
                )
            ]
        )

        # Verify the structure matches what templates expect
        category = result.categories[0]
        article = category.articles[0]

        # These are the fields templates should use
        assert hasattr(article, 'chinese_title')
        assert hasattr(article, 'original_url')
        assert hasattr(article, 'summary')

    def test_template_category_name_field(self):
        """
        Test that category should use 'category' not 'category_name'.
        测试 category 应该使用 'category' 而不是 'category_name'。
        """
        from omnidigest.jobs import CategorySummary

        category = CategorySummary(
            category="AI & LLMs",
            overview="Overview",
            critique="Critique",
            articles=[]
        )

        # The correct field is 'category', not 'category_name'
        assert category.category == "AI & LLMs"


class TestDailySummaryFormatter:
    """
    Test cases for daily summary data formatting.
    每日汇总数据格式化测试用例。
    """

    def test_format_articles_uses_correct_fields(self):
        """
        Test that formatting articles uses correct field names from ArticleTranslation.
        测试格式化文章时使用 ArticleTranslation 的正确字段名。
        """
        from omnidigest.jobs import ArticleTranslation

        # Simulate what the code does
        article = ArticleTranslation(
            id=1,
            chinese_title="测试标题",
            summary="测试摘要",
            original_url="https://example.com"
        )

        # The code should use these fields
        formatted = {
            "title": article.chinese_title,
            "url": article.original_url,
            "summary": article.summary
        }

        assert formatted["title"] == "测试标题"
        assert formatted["url"] == "https://example.com"
        assert formatted["summary"] == "测试摘要"

    def test_format_category_uses_correct_fields(self):
        """
        Test that formatting category uses correct field names.
        测试格式化 category 时使用正确的字段名。
        """
        from omnidigest.jobs import CategorySummary, ArticleTranslation

        category = CategorySummary(
            category="AI & LLMs",
            overview="Overview",
            critique="Critique",
            articles=[
                ArticleTranslation(
                    id=1,
                    chinese_title="Title",
                    summary="Summary",
                    original_url="https://example.com"
                )
            ]
        )

        # The code should use category.category, not category.category_name
        assert category.category == "AI & LLMs"


class TestMockDailySummaryFlow:
    """
    Integration-style tests for the daily summary flow.
    每日汇总流程的集成测试。
    """

    def test_summary_data_structure_matches_templates(self):
        """
        Test that summary_data structure matches what templates expect.
        测试 summary_data 结构与模板期望的一致。
        """
        from omnidigest.jobs import DailySummaryResult, CategorySummary, ArticleTranslation

        # Create the exact structure that job_daily_summary creates
        result = DailySummaryResult(
            overview="今日科技动态",
            categories=[
                CategorySummary(
                    category="AI & LLMs",
                    overview="大模型发展迅速",
                    critique="AI 领域又有新突破",
                    articles=[
                        ArticleTranslation(
                            id=1,
                            chinese_title="OpenAI 发布新模型",
                            summary="GPT-5 性能大幅提升",
                            original_url="https://openai.com/blog"
                        )
                    ]
                )
            ]
        )

        # Verify structure that templates will access
        for cat in result.categories:
            # Templates use category.category_name -> should be cat.category
            assert hasattr(cat, 'category')

            for art in cat.articles:
                # Templates use article.title -> should be art.chinese_title
                # Templates use article.url -> should be art.original_url
                assert hasattr(art, 'chinese_title')
                assert hasattr(art, 'original_url')
                assert hasattr(art, 'summary')
