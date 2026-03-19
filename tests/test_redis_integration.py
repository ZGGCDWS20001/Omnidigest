"""
Redis cache integration tests.
Redis 缓存集成测试。

测试 Redis 连接状态和性能。
"""
import pytest
import time


class TestRedisConfig:
    """
    Test Redis configuration.
    Redis 配置测试。
    """

    def test_redis_is_enabled(self):
        """
        Test if Redis is enabled in settings.
        测试 Redis 是否在设置中启用。
        """
        from omnidigest.config import settings

        # Check redis_enabled setting
        assert hasattr(settings, 'redis_enabled'), "Settings should have redis_enabled attribute"
        print(f"\nRedis enabled: {settings.redis_enabled}")

    def test_redis_connection_config(self):
        """
        Test Redis connection configuration.
        测试 Redis 连接配置。
        """
        from omnidigest.config import settings

        # Verify Redis configuration exists
        assert hasattr(settings, 'redis_host'), "Settings should have redis_host"
        assert hasattr(settings, 'redis_port'), "Settings should have redis_port"
        assert hasattr(settings, 'redis_db'), "Settings should have redis_db"

        print(f"\nRedis config: {settings.redis_host}:{settings.redis_port}/{settings.redis_db}")

    @pytest.mark.integration
    def test_redis_actual_connection(self):
        """
        Test actual Redis connection.
        测试实际 Redis 连接。
        """
        from omnidigest.config import settings

        if not settings.redis_enabled:
            pytest.skip("Redis is not enabled")

        try:
            import redis
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password or None,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

            # Test ping
            result = client.ping()
            assert result is True, "Redis ping should return True"

            print(f"\n✓ Redis connection successful: {settings.redis_host}:{settings.redis_port}")

        except redis.ConnectionError as e:
            pytest.fail(f"Redis connection failed: {e}")
        except Exception as e:
            pytest.fail(f"Redis test failed: {e}")


class TestRedisPerformance:
    """
    Test Redis performance metrics.
    Redis 性能指标测试。
    """

    @pytest.fixture
    def redis_client(self):
        """
        Create a Redis client for testing.
        创建测试用 Redis 客户端。
        """
        from omnidigest.config import settings

        if not settings.redis_enabled:
            pytest.skip("Redis is not enabled")

        try:
            import redis
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password or None,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

            # Verify connection
            client.ping()

            yield client

            # Cleanup
            client.delete("test:performance:*")

        except redis.ConnectionError:
            pytest.skip("Redis is not available")

    @pytest.mark.integration
    def test_set_operation_speed(self, redis_client):
        """
        Test SET operation speed.
        测试 SET 操作速度。
        """
        key = "test:performance:set"
        value = "test_value"

        # Warm up
        redis_client.set(key, value)

        # Measure speed
        iterations = 1000
        start_time = time.perf_counter()

        for i in range(iterations):
            redis_client.set(key, f"{value}_{i}")

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        ops_per_sec = iterations / elapsed

        print(f"\nSET operations: {iterations} in {elapsed:.4f}s")
        print(f"Performance: {ops_per_sec:.0f} ops/sec")

        # Assert reasonable performance (at least 100 ops/sec)
        assert ops_per_sec > 100, f"Too slow: {ops_per_sec:.0f} ops/sec"

    @pytest.mark.integration
    def test_get_operation_speed(self, redis_client):
        """
        Test GET operation speed.
        测试 GET 操作速度。
        """
        key = "test:performance:get"

        # Prepare data
        value = "test_value" * 100  # 1KB data
        redis_client.set(key, value)

        # Measure speed
        iterations = 1000
        start_time = time.perf_counter()

        for _ in range(iterations):
            redis_client.get(key)

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        ops_per_sec = iterations / elapsed

        print(f"\nGET operations: {iterations} in {elapsed:.4f}s")
        print(f"Performance: {ops_per_sec:.0f} ops/sec")

        # Assert reasonable performance
        assert ops_per_sec > 100, f"Too slow: {ops_per_sec:.0f} ops/sec"

    @pytest.mark.integration
    def test_mset_operation_speed(self, redis_client):
        """
        Test MSET (multi-set) operation speed.
        测试 MSET (批量设置) 操作速度。
        """
        iterations = 100
        start_time = time.perf_counter()

        for i in range(iterations):
            redis_client.mset({
                f"test:performance:mset:{i}:key1": "value1",
                f"test:performance:mset:{i}:key2": "value2",
                f"test:performance:mset:{i}:key3": "value3",
            })

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        ops_per_sec = iterations / elapsed

        print(f"\nMSET operations: {iterations} in {elapsed:.4f}s")
        print(f"Performance: {ops_per_sec:.0f} ops/sec")

        # Cleanup
        redis_client.delete("test:performance:mset:*")

        assert ops_per_sec > 50, f"Too slow: {ops_per_sec:.0f} ops/sec"

    @pytest.mark.integration
    def test_ping_latency(self, redis_client):
        """
        Test Redis ping latency.
        测试 Redis ping 延迟。
        """
        iterations = 100
        latencies = []

        for _ in range(iterations):
            start = time.perf_counter()
            redis_client.ping()
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)

        print(f"\nPing latency (ms):")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  Min: {min_latency:.2f}ms")
        print(f"  Max: {max_latency:.2f}ms")

        # Assert reasonable latency (average < 10ms)
        assert avg_latency < 10, f"Too high latency: {avg_latency:.2f}ms"

    @pytest.mark.integration
    def test_connection_pool_performance(self, redis_client):
        """
        Test connection pool performance.
        测试连接池性能。
        """
        from omnidigest.config import settings
        import redis

        # Create connection pool
        pool = redis.ConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            max_connections=10,
        )

        iterations = 500

        # Test with connection pool
        start_time = time.perf_counter()
        for i in range(iterations):
            client = redis.Redis(connection_pool=pool)
            client.ping()
            client.close()

        end_time = time.perf_counter()
        elapsed = end_time - start_time
        ops_per_sec = iterations / elapsed

        print(f"\nConnection pool: {iterations} in {elapsed:.4f}s")
        print(f"Performance: {ops_per_sec:.0f} ops/sec")

        # Cleanup
        pool.disconnect()

        assert ops_per_sec > 50, f"Too slow: {ops_per_sec:.0f} ops/sec"


class TestRedisDataOperations:
    """
    Test Redis data operations.
    Redis 数据操作测试。
    """

    @pytest.fixture
    def redis_client(self):
        """
        Create a Redis client for testing.
        """
        from omnidigest.config import settings

        if not settings.redis_enabled:
            pytest.skip("Redis is not enabled")

        try:
            import redis
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password or None,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            client.ping()

            yield client

            # Cleanup
            client.delete("test:data:*")

        except redis.ConnectionError:
            pytest.skip("Redis is not available")

    @pytest.mark.integration
    def test_string_operations(self, redis_client):
        """
        Test string data operations.
        测试字符串数据操作。
        """
        # SET/GET
        redis_client.set("test:data:string", "hello")
        assert redis_client.get("test:data:string") == "hello"

        # SETEX
        redis_client.setex("test:data:expire", 60, "expire_test")
        assert redis_client.get("test:data:expire") == "expire_test"

        # INCR/DECR
        redis_client.set("test:data:counter", "10")
        redis_client.incr("test:data:counter")
        assert redis_client.get("test:data:counter") == "11"

        print("\n✓ String operations working correctly")

    @pytest.mark.integration
    def test_hash_operations(self, redis_client):
        """
        Test hash data operations.
        测试哈希数据操作。
        """
        # HSET/HGET
        redis_client.hset("test:data:hash", mapping={
            "field1": "value1",
            "field2": "value2",
        })

        assert redis_client.hget("test:data:hash", "field1") == "value1"
        assert redis_client.hget("test:data:hash", "field2") == "value2"

        # HGETALL
        all_data = redis_client.hgetall("test:data:hash")
        assert len(all_data) == 2

        print("\n✓ Hash operations working correctly")

    @pytest.mark.integration
    def test_list_operations(self, redis_client):
        """
        Test list data operations.
        测试列表数据操作。
        """
        # LPUSH/RPUSH
        redis_client.delete("test:data:list")
        redis_client.lpush("test:data:list", "first")
        redis_client.rpush("test:data:list", "last")

        # LRANGE
        items = redis_client.lrange("test:data:list", 0, -1)
        assert items == ["first", "last"]

        # LLEN
        assert redis_client.llen("test:data:list") == 2

        print("\n✓ List operations working correctly")

    @pytest.mark.integration
    def test_set_operations(self, redis_client):
        """
        Test set data operations.
        测试集合数据操作。
        """
        # SADD
        redis_client.sadd("test:data:set", "member1", "member2", "member3")

        # SISMEMBER
        assert redis_client.sismember("test:data:set", "member1") == 1
        assert redis_client.sismember("test:data:set", "member4") == 0

        # SMEMBERS
        members = redis_client.smembers("test:data:set")
        assert len(members) == 3

        print("\n✓ Set operations working correctly")

    @pytest.mark.integration
    def test_expiry_operations(self, redis_client):
        """
        Test key expiry operations.
        测试键过期操作。
        """
        # SET with expiry
        redis_client.setex("test:data:ttl", 1, "expires")

        # Verify TTL exists
        ttl = redis_client.ttl("test:data:ttl")
        assert ttl > 0, "TTL should be positive"

        # Wait for expiry
        time.sleep(1.5)

        # Verify key expired
        value = redis_client.get("test:data:ttl")
        assert value is None, "Key should have expired"

        print("\n✓ Expiry operations working correctly")


# Mark integration tests
pytestmark = pytest.mark.integration
