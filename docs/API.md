# OmniDigest API 接口文档

## 基础信息

- **Base URL**: `http://localhost:7080/api`
- **认证**: 除 `/health` 和 `/webhook/telegram` 外都需要 `X-API-Key` 请求头

## 认证方式

在请求头中添加：
```
X-API-Key: test_client:degymFyHGCmzcffDTJTDa9vKBcf8TdUR_GGJdOwSUsc
```

---

## 完整 API 端点列表

### 1. 健康检查

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/health` | 服务健康检查 | ❌ |

---

### 2. 任务触发 (Trigger)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| POST | `/api/trigger/fetch` | 触发新闻抓取 | ✅ |
| POST | `/api/trigger/process` | 触发内容处理 | ✅ |
| POST | `/api/trigger/kg_extract` | 触发知识图谱提取 | ✅ |
| POST | `/api/trigger/summary` | 触发每日摘要 | ✅ |
| POST | `/api/trigger/summary/telegram` | 触发 Telegram 摘要推送 | ✅ |
| POST | `/api/trigger/summary/dingtalk` | 触发钉钉摘要推送 | ✅ |
| POST | `/api/trigger/sync/rag` | 触发 RAG 同步 | ✅ |

---

### 3. 统计模块 (Stats)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/stats/overview` | 概览统计 | ✅ |
| GET | `/api/stats/articles` | 文章统计 | ✅ |
| GET | `/api/stats/breaking` | 突发新闻统计 | ✅ |
| GET | `/api/stats/twitter` | Twitter 统计 | ✅ |
| GET | `/api/stats/llm` | LLM 使用统计 | ✅ |

---

### 4. Token 统计

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/token-stats` | Token 使用统计 | ✅ |
| GET | `/api/token-stats/range` | Token 统计（按范围） | ✅ |

---

### 5. 配置管理 (Config)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/config` | 获取所有配置 | ✅ |
| GET | `/api/config/{section}` | 获取指定section配置 | ✅ |
| GET | `/api/config/{section}/{key}` | 获取指定key值 | ✅ |
| PUT | `/api/config/{section}` | 更新section配置 | ✅ |
| POST | `/api/config` | 创建新配置 | ✅ |
| DELETE | `/api/config/{section}/{key}` | 删除配置 | ✅ |

---

### 6. 源管理 (Sources)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/sources` | 获取所有源 | ✅ |
| GET | `/api/sources/rss` | 获取RSS源列表 | ✅ |
| POST | `/api/sources/rss` | 添加RSS源 | ✅ |
| PUT | `/api/sources/rss/{source_id}` | 更新RSS源 | ✅ |
| DELETE | `/api/sources/rss/{source_id}` | 删除RSS源 | ✅ |
| POST | `/api/sources/rss/{source_id}/toggle` | 切换源启用状态 | ✅ |

---

### 7. 认证管理 (Auth)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/auth/keys` | 获取所有 API Key | ✅ |
| POST | `/api/auth/keys` | 创建新的 API Key | ✅ |
| DELETE | `/api/auth/keys/{client_name}` | 删除 API Key | ✅ |
| POST | `/api/auth/keys/{client_name}/activate` | 激活 API Key | ✅ |

---

### 8. 知识图谱 (Knowledge Graph)

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/kg/status` | 知识图谱状态 | ✅ |
| GET | `/api/kg/stats` | 知识图谱统计 | ✅ |
| GET | `/api/kg/entities` | 查询实体 | ✅ |
| GET | `/api/kg/entity/{uid}` | 获取实体详情 | ✅ |
| GET | `/api/kg/relations` | 查询关系 | ✅ |
| GET | `/api/kg/search` | 搜索路径 | ✅ |

---

### 9. A股市场 (A-Stock) ⭐

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| GET | `/api/astock/quotes` | 实时行情（大盘） | ✅ |
| GET | `/api/astock/sectors` | 板块涨跌排行 | ✅ |
| GET | `/api/astock/news` | 财经新闻 | ✅ |
| GET | `/api/astock/analysis/latest` | 最新分析结果 | ✅ |
| GET | `/api/astock/accuracy` | 准确率统计 | ✅ |
| POST | `/api/astock/analysis/trigger` | 手动触发分析 | ✅ |
| GET | `/api/astock/stocks/{symbol}` | 个股实时行情 | ✅ |
| GET | `/api/astock/stocks/{symbol}/news` | 个股相关新闻 | ✅ |
| GET | `/api/astock/stocks/{symbol}/predictions` | 个股预测 | ✅ |
| GET | `/api/astock/alert/check` | 异常波动检测 | ✅ |
| GET | `/api/astock/alert/status` | 告警配置状态 | ✅ |

#### A股 API 响应示例

**GET /api/astock/quotes**
```json
{
  "market_session": "closed",
  "market_open": false,
  "shanghai": {
    "name": "上证指数",
    "symbol": "sh000001",
    "price": 4062.98,
    "change": 0.32,
    "volume": 623873102,
    "turnover": 876327491360
  },
  "shenzhen": {
    "name": "深证成指",
    "symbol": "sz399001",
    "price": 14187.80,
    "change": 1.05
  }
}
```

**GET /api/astock/sectors**
```json
{
  "sectors": [
    {"name": "人工智能", "change": 3.45, "volume": 125000000, "turnover": 89000000000},
    {"name": "新能源汽车", "change": 2.18}
  ],
  "update_time": "2026-03-19T03:31:54"
}
```

**GET /api/astock/news**
```json
{
  "news": [
    {
      "id": "uuid",
      "title": "道指深夜跌超400点...",
      "content": "...",
      "source": "21世纪经济报道",
      "url": "",
      "publish_time": "2026-03-18T14:31:00",
      "symbols": [],
      "sectors": []
    }
  ],
  "total": 5
}
```

---

### 10. 分析与 Webhook

| 方法 | 完整路径 | 说明 | 认证 |
|------|----------|------|------|
| POST | `/api/analyze/trends` | 趋势分析 | ✅ |
| POST | `/api/webhook/telegram` | Telegram Webhook | ❌ |

---

## 总结

- **总计**: 51 个 API 端点
- **需要认证**: 49 个
- **无需认证**: 2 个 (`/health`, `/webhook/telegram`)

---

## 错误响应

```json
{"error": "错误信息"}
```
