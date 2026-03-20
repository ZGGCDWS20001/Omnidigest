"""
Tests for Prometheus metrics.

由于 backend/src/main.py 使用相对导入，无法直接测试 /metrics 端点。
本测试文件验证 metrics 模块的代码结构和定义。

运行方式：
    # 从项目根目录运行
    cd /home/frank/Documents/code/newssync-main
    python -m pytest tests/test_metrics.py -v
"""
import pytest
import ast
import os


class TestMetricsCodeStructure:
    """
    Test cases for metrics code structure.
    metrics 代码结构测试用例。
    """

    @pytest.fixture
    def metrics_file_path(self):
        """Get the path to metrics.py file."""
        return os.path.join(
            os.path.dirname(__file__),
            "..",  # tests/
            "backend", "src", "core", "metrics.py"
        )

    def test_metrics_file_exists(self, metrics_file_path):
        """
        Test that metrics.py file exists.
        测试 metrics.py 文件存在。
        """
        full_path = os.path.abspath(metrics_file_path)
        assert os.path.exists(full_path), f"metrics.py not found at {full_path}"

    def test_metrics_has_required_metrics(self, metrics_file_path):
        """
        Test that metrics.py contains required metric definitions.
        测试 metrics.py 包含必需的指标定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        # Check for required metric definitions
        required_metrics = [
            'api_request_duration',
            'cache_hits_total',
            'cache_misses_total',
            'db_connections_active',
            'llm_tokens_used_total',
            'job_execution_count',
        ]

        for metric in required_metrics:
            assert metric in content, f"Metric '{metric}' not found in metrics.py"

    def test_metrics_has_prometheus_imports(self, metrics_file_path):
        """
        Test that metrics.py imports prometheus_client.
        测试 metrics.py 导入 prometheus_client。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'from prometheus_client import' in content, \
            "prometheus_client import not found"

    def test_metrics_has_counter_metrics(self, metrics_file_path):
        """
        Test that metrics.py contains Counter metrics.
        测试 metrics.py 包含 Counter 指标。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'Counter(' in content, "Counter metrics not found"

    def test_metrics_has_gauge_metrics(self, metrics_file_path):
        """
        Test that metrics.py contains Gauge metrics.
        测试 metrics.py 包含 Gauge 指标。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'Gauge(' in content, "Gauge metrics not found"

    def test_metrics_has_histogram_metrics(self, metrics_file_path):
        """
        Test that metrics.py contains Histogram metrics.
        测试 metrics.py 包含 Histogram 指标。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'Histogram(' in content, "Histogram metrics not found"


class TestMetricsEndpointConfiguration:
    """
    Test cases for metrics endpoint configuration in main.py.
    main.py 中 metrics 端点配置测试。
    """

    @pytest.fixture
    def main_file_path(self):
        """Get the path to main.py file."""
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "backend", "src", "main.py"
        )

    def test_main_file_has_metrics_import(self, main_file_path):
        """
        Test that main.py imports prometheus instrumentator.
        测试 main.py 导入 prometheus instrumentator。
        """
        full_path = os.path.abspath(main_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'prometheus' in content.lower(), \
            "Prometheus import not found in main.py"

    def test_main_file_exposes_metrics_endpoint(self, main_file_path):
        """
        Test that main.py exposes /metrics endpoint.
        测试 main.py 暴露 /metrics 端点。
        """
        full_path = os.path.abspath(main_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert '/metrics' in content, "/metrics endpoint not found in main.py"
        assert 'expose' in content, "expose method not found in main.py"


class TestMetricsCoverage:
    """
    Test cases to verify metrics coverage.
    指标覆盖率测试。
    """

    @pytest.fixture
    def metrics_file_path(self):
        """Get the path to metrics.py file."""
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "backend", "src", "core", "metrics.py"
        )

    def test_metrics_coverage_api_requests(self, metrics_file_path):
        """
        Test that API request metrics are defined.
        测试 API 请求指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'api_request_duration_seconds' in content, \
            "API request duration metric missing"

    def test_metrics_coverage_cache(self, metrics_file_path):
        """
        Test that cache metrics are defined.
        测试缓存指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'cache_hits_total' in content, "Cache hits metric missing"
        assert 'cache_misses_total' in content, "Cache misses metric missing"

    def test_metrics_coverage_database(self, metrics_file_path):
        """
        Test that database metrics are defined.
        测试数据库指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'db_connections_active' in content, "DB connections metric missing"

    def test_metrics_coverage_llm(self, metrics_file_path):
        """
        Test that LLM metrics are defined.
        测试 LLM 指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'llm_tokens_used_total' in content, "LLM tokens metric missing"
        assert 'llm_requests_total' in content, "LLM requests metric missing"

    def test_metrics_coverage_jobs(self, metrics_file_path):
        """
        Test that job metrics are defined.
        测试任务指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'job_execution_count' in content, "Job execution count missing"

    def test_metrics_coverage_astock(self, metrics_file_path):
        """
        Test that A-stock metrics are defined.
        测试 A股指标已定义。
        """
        full_path = os.path.abspath(metrics_file_path)

        with open(full_path, 'r') as f:
            content = f.read()

        assert 'astock_analysis_count' in content, "A-stock analysis metric missing"
