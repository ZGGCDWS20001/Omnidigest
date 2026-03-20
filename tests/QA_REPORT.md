# OmniDigest QA 测试报告

**测试日期**: 2026-03-20
**测试人员**: QA Engineer
**项目**: OmniDigest 新闻情报平台

---

## 测试执行摘要

由于权限限制，无法运行 pytest 进行自动化测试。进行了**代码质量审查**来验证 TEST_SPEC.md 中定义的测试点。

---

## 代码审查结果

### ✅ Test 1.1: Twitter Dead Code Removal
**状态**: PASS
**文件**: `backend/src/domains/twitter/processor.py`
**结果**: 无死代码问题。代码逻辑正常。

---

### ✅ Test 1.2: Twitter 新事件阈值逻辑
**状态**: PASS
**文件**: `backend/src/domains/twitter/processor.py:136-142`
**结果**:
- 新事件创建后，`source_count = 1`
- 当 `threshold == 1` 时立即返回事件进行推送
- 当 `threshold > 1` 时返回 None，不推送
- 逻辑正确

---

### ✅ Test 1.3: 现有事件阈值逻辑
**状态**: PASS
**文件**: `backend/src/domains/twitter/processor.py:250-258`
**结果**:
- 现有事件增加 `source_count` 后
- 当 `new_count >= threshold` 时返回事件进行推送
- 逻辑正确

---

### ✅ Test 2.1: 分类后状态更新
**状态**: PASS
**文件**: `backend/src/domains/daily_digest/db_repo.py:178-180`
**结果**:
```sql
UPDATE news_articles
SET category = %s, score = %s, summary_raw = %s, status = 1
WHERE id = %s
```
- 分类后正确设置 `status = 1`
- 满足要求

---

### ✅ Test 2.2: RAG 上传失败处理
**状态**: PASS
**文件**: `backend/src/domains/ingestion/rss/standard_crawler.py:182-185`
**结果**:
```python
else:
    # Handle RAG upload failure - still mark as processed to avoid limbo
    self.db.update_status(article_id, 1, ragflow_id=None)
```
- RAG 上传失败时仍标记为已处理 (`status = 1`)
- 满足要求

---

### ✅ Test 2.3: 防止重复分类
**状态**: PASS
**文件**: `backend/src/domains/daily_digest/db_repo.py:149-155`
**结果**:
```sql
SELECT ... FROM news_articles
WHERE category IS NULL
```
- 只返回 `category IS NULL` 的未分类文章
- 防止重复分类，满足要求

---

### ⚠️ Test 3.1: Story Source Count
**状态**: 需要确认
**文件**: `backend/src/domains/breaking_news/db_repo.py:275-276`
**结果**:
```sql
SELECT COUNT(DISTINCT r.source_url) as cnt
```

**差异发现**:
- TEST_SPEC.md 要求使用 `DISTINCT r.source_platform` (按平台计数)
- 代码实际使用 `DISTINCT r.source_url` (按来源URL计数)

**数据库表结构**: `breaking_stream_raw` 同时包含 `source_platform` 和 `source_url` 字段。

**建议**: 确认业务需求是按"平台"还是"URL"计数。如果需要按平台计数，需要修改代码。

---

### ✅ Test 3.2: 验证状态更新
**状态**: PASS
**文件**: `backend/src/domains/breaking_news/db_repo.py:325-330`
**结果**:
```python
status = 'verified' if source_count >= 2 else 'developing'
```

| source_count | 预期状态 | 实际状态 |
|-------------|---------|---------|
| 0           | developing | developing |
| 1           | developing | developing |
| 2           | verified   | verified   |
| 5           | verified   | verified   |

- 满足要求

---

## 测试覆盖率

| 测试类别 | 通过 | 失败 | 待确认 |
|---------|------|------|--------|
| Twitter 事件处理 | 3 | 0 | 0 |
| Daily Digest | 3 | 0 | 0 |
| Breaking News | 1 | 0 | 1 |
| **总计** | **7** | **0** | **1** |

---

## 发现的问题

### 问题 #1: Breaking News Source Count 字段不一致
- **严重程度**: 中
- **描述**: `get_story_source_count()` 使用 `source_url` 计数，与 TEST_SPEC.md 要求的 `source_platform` 不一致
- **影响**: 如果业务需求是按"独立平台"计数，则当前实现会按"独立URL"计数，结果可能不同
- **建议**: 确认业务需求，如有需要修改代码

---

## 结论

代码整体质量良好，7/8 测试点通过验证。1个测试点需要业务确认。

**建议**:
1. 确认 Breaking News 的 source_count 是按平台还是 URL 计数
2. 如果权限允许，运行实际测试验证代码行为
