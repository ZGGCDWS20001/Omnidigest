# 前端 API 调用排查报告

## 1. 当前状态

### 1.1 配置文件状态

| 文件 | 状态 | 说明 |
|-----|------|------|
| `api/index.js` | ✅ 正常 | baseURL = '/api' |
| `vite.config.js` | ✅ 正常 | 代理 /api -> localhost:7080 |

### 1.2 API 测试结果

| API 端点 | 状态 | 说明 |
|---------|------|------|
| `/api/stats/overview` | ✅ 200 OK | Dashboard 数据 |
| `/api/stats/breaking` | ✅ 200 OK | 突发事件数据 |
| `/api/stats/twitter` | ✅ 200 OK | Twitter 事件 |
| `/api/token-stats/range` | ✅ 200 OK | Token 统计 |
| `/api/astock/quotes` | ✅ 200 OK | A股行情 |
| `/api/astock/sectors` | ✅ 200 OK | 板块排行 |
| `/api/astock/news` | ✅ 200 OK | 财经新闻 |
| `/api/astock/accuracy` | ✅ 200 OK | 准确率统计 |
| `/api/kg/status` | ✅ 200 OK | 知识图谱状态 |
| `/api/sources/rss` | ✅ 200 OK | RSS 源列表 |
| `/api/config` | ✅ 200 OK | 配置列表 |

### 1.3 前端 View 调用检查

| View 文件 | 使用的 API | 状态 |
|-----------|-----------|------|
| Dashboard.vue | statsApi | ✅ 使用正确 |
| AStock.vue | astockApi | ✅ 使用正确 |
| StockDetail.vue | astockApi | ✅ 使用正确 |
| TokenStats.vue | statsApi | ✅ 使用正确 |
| Sources.vue | sourcesApi | ✅ 使用正确 |
| Config.vue | configApi | ✅ 使用正确 |
| KnowledgeGraph.vue | kgApi | ✅ 使用正确 |

---

## 2. 已修复问题

### 2.1 Dashboard.vue - 直接使用 api.get()

**问题**: 直接使用 `api.get('/token-stats/range?hours=24')` 而非 `statsApi.tokenStatsByRange()`

**修复**: 已改用 `statsApi.tokenStatsByRange(null, null, 24)`

**状态**: ✅ 已修复

---

## 3. API Key 认证

### 3.1 认证方式

- 前端通过 axios interceptor 自动添加 `X-API-Key` 请求头
- 存储在 localStorage 中，格式: `client_name:key`

### 3.2 测试用 API Key

```
test_client:degymFyHGCmzcffDTJTDa9vKBcf8TdUR_GGJdOwSUsc
```

### 3.3 401 处理

- 后端返回 401 时，前端自动弹出 API Key 输入框
- 错误处理逻辑: `api/index.js` 第 31-40 行

---

## 4. 代理配置

### 4.1 Vite 代理

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:7080',
    changeOrigin: true
  }
}
```

### 4.2 请求流程

```
前端调用: api.get('/stats/overview')
    ↓
baseURL + 路径: /api/stats/overview
    ↓
Vite 代理: /api/* -> http://localhost:7080/api/*
    ↓
后端接收: /api/stats/overview
```

---

## 5. 结论

**API 路径配置正确，所有端点均可正常访问。**

如遇问题，请检查：
1. 后端服务是否运行在端口 7080
2. localStorage 中的 API Key 是否正确
3. 浏览器控制台是否有 JS 报错

---

## 6. 常见问题排查

### 6.1 页面显示数据为空

**排查步骤**：
1. 打开浏览器开发者工具 (F12) → Console 标签
2. 查看是否有 API 响应日志
3. 检查 Network 标签中 API 请求的响应内容
4. 确认 `localStorage.getItem('api_key')` 有值

### 6.2 API 请求 401 错误

**原因**：API Key 无效或过期

**解决**：
```javascript
// 在 Console 中重新设置
localStorage.setItem('api_key', 'test_client:degymFyHGCmzcffDTJTDa9vKBcf8TdUR_GGJdOwSUsc')
// 刷新页面
```

### 6.3 Vite 热更新不生效

**原因**：某些配置更改后需要重启开发服务器

**解决**：
```bash
# 重启 Vite
pkill -f "vite"
npm run dev
```
