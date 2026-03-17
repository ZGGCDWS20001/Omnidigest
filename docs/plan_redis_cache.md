# Redis 缓存方案

## 1. 缓存策略分析

### 适合缓存的 API 端点（读多改少）

| 端点 | 描述 | 缓存时间建议 |
|------|------|-------------|
| `GET /stats/overview` | 系统概览（文章数、事件数、Token使用） | 60 秒 |
| `GET /stats/articles` | 文章统计（分类、分数分布） | 60 秒 |
| `GET /stats/breaking` | Breaking News 统计 | 30 秒 |
| `GET /stats/twitter` | Twitter 统计 | 30 秒 |
| `GET /stats/llm` | LLM 模型状态 | 60 秒 |
| `GET /config` | 全局配置 | 300 秒 |
| `GET /config/{section}` | 配置节 | 300 秒 |
| `GET /sources/rss` | RSS 源列表 | 60 秒 |
| `GET /auth/keys` | API Key 列表 | 60 秒 |
| `GET /kg/stats` | 知识图谱统计 | 60 秒 |

### 不适合缓存的端点

- 所有 `/trigger/*` 端点（触发写入操作）
- 所有 `POST/PUT/DELETE` 写操作端点
- `/health` 健康检查（直接查库）

---

## 2. Redis 数据结构设计

### 键命名规则
```
格式: omnidigest:{resource}:{id}:{field}
示例:
  omnidigest:stats:overview
  omnidigest:stats:articles:7days
  omnidigest:config:breaking
  omnidigest:sources:rss:list
  omnidigest:kg:stats
```

### 过期时间 (TTL)

| 资源类型 | TTL | 说明 |
|----------|-----|------|
| stats/* | 30-60s | 实时数据，短缓存 |
| config/* | 300s | 配置不常变化 |
| sources/* | 60s | 源状态可能变化 |
| kg/* | 60s | 图谱更新频繁 |

### 序列化方式
- **JSON**: 用于复杂结构（stats、config）
- **String**: 用于简单值

---

## 3. 缓存失效机制

### 方案 A: 主动失效（推荐）
在写操作后主动删除相关缓存键：

```python
# 示例：更新配置后清除缓存
def update_config(section, items):
    db.update_config(section, items)
    redis.delete(f"omnidigest:config")
    redis.delete(f"omnidigest:config:{section}")
```

### 方案 B: 被动过期
使用 Redis TTL 自动过期，无需手动清除。

### 建议
- **config**: 使用主动失效 + 较长 TTL (300s)
- **stats**: 使用被动过期 + 短 TTL (30-60s)
- **sources**: 使用主动失效（添加/修改源时清除）

---

## 4. 实现步骤

### Step 1: 添加 Redis 依赖
```bash
# requirements.txt
redis>=5.0.0
```

### Step 2: 添加 Redis 配置
```python
# config.py
class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None
```

### Step 3: 创建缓存服务
```python
# src/omnidigest/core/cache.py
import redis
import json
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self.client = redis.Redis(...)

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: Any, ttl: int = 60):
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        self.client.delete(key)

    def delete_pattern(self, pattern: str):
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)
```

### Step 4: 集成到 API 路由
```python
# 在 router.py 中使用缓存
@router.get("/stats/overview")
def get_stats_overview():
    cache_key = "omnidigest:stats:overview"
    cached = cache.get(cache_key)
    if cached:
        return cached

    data = fetch_from_db()
    cache.set(cache_key, data, ttl=60)
    return data
```

### Step 5: 更新写操作清除缓存
```python
@router.put("/config/{section}")
def update_config(section, items):
    result = db.update_config(section, items)
    # 清除相关缓存
    cache.delete("omnidigest:config")
    cache.delete(f"omnidigest:config:{section}")
    return result
```

---

## 5. Docker Compose 配置

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    container_name: omnidigest_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - omnidigest_network

  omnidigest:
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379

volumes:
  redis_data:
```

---

## 6. 预期效果

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 打开 Dashboard | 3-5 次 DB 查询 (~200ms) | 1 次 Redis 查询 (~5ms) |
| 刷新 Token Stats | DB 聚合查询 (~150ms) | Redis 缓存 (~5ms) |
| 切换配置页面 | DB 查询 (~50ms) | Redis 缓存 (~5ms) |

**预计性能提升: 10-50 倍**
