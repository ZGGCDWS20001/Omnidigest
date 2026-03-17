# Dgraph 知识图谱查询指南 (DQL)

本指南包含了在 OmniDigest 知识图谱 (v1.5.0) 中常用的 Dgraph 查询语言 (DQL) 示例。您可以在 Dgraph Ratel UI (默认为 `http://localhost:8000`) 的 Console 面板中直接运行这些查询，也可以通过 HTTP API 发送请求。

## 1. 基础探索查询

### 1.1 查看图中所有的节点类型统计
```graphql
{
  node_stats(func: has(dgraph.type)) {
    type: dgraph.type
    count(uid)
  }
}
```

### 1.2 随机抽取几条事件 (Event)
```graphql
{
  recent_events(func: type(Event), first: 5) {
    uid
    title
    summary
    category
    event_date
  }
}
```

## 2. 实体 (Entity) 查询

### 2.1 通过名称精确查找人物 (Person)
```graphql
{
  find_person(func: eq(name, "特朗普")) @filter(type(Person)) {
    uid
    name
    description
    mentioned_in {
      uid
      title
      event_date
    }
  }
}
```

### 2.2 通过前缀/全文本搜索组织 (Organization)
*注意：全文本搜索会对分词进行匹配。*
```graphql
{
  search_org(func: anyofterms(name, "Google 谷歌 Apple")) @filter(type(Organization)) {
    uid
    name
    description
  }
}
```

## 3. 关系与网络级联查询

### 3.1 查找一个事件 (Event) 涉及的所有实体
```graphql
{
  event_details(func: type(Event), first: 3) {
    uid
    title
    event_date
    involves_person {
      name
      description
    }
    involves_org {
      name
    }
    located_at {
      name
    }
  }
}
```

### 3.2 查找一个人物 (Person) 参与的所有事件及其分类
```graphql
{
  person_activity(func: eq(name, "埃隆·马斯克")) @filter(type(Person)) {
    name
    mentioned_in {
      title
      category
      event_date
    }
  }
}
```

### 3.3 查找多个实体共同参与的交集事件 (多条件过滤)
查找同时包含“苹果”和“库克”的事件：
```graphql
{
  var(func: eq(name, "苹果")) {
    events_org as mentioned_in
  }
  var(func: eq(name, "蒂姆·库克")) {
    events_person as mentioned_in
  }

  intersection_events(func: uid(events_org)) @filter(uid(events_person)) {
    uid
    title
    event_date
  }
}
```

## 4. 图谱清理与维护

### 4.1 查找孤立的实体 (没有关联任何事件的尸体节点)
```graphql
{
  isolated_entities(func: has(name)) @filter(NOT has(mentioned_in)) {
    uid
    name
    dgraph.type
  }
}
```

### 4.2 通过 UID 删除一个特定的节点
*(注意：这是一个 Mutation，需要在 Ratel 的 Mutation 选填框执行，或者通过 pydgraph/curl)*
```json
{
  "delete": [
    {
      "uid": "0x12a"
    }
  ]
}
```

## 5. 复杂趋势分析查询

### 5.1 按分类统计事件中被提及最多的组织 (Top Organizations by Category)
这通常需要客户端辅助，但在 Dgraph 里可以拉取分组数据：
```graphql
{
  events_by_cat(func: type(Event)) @groupby(category) {
    count(uid)
  }
  
  all_orgs(func: type(Organization)) {
    name
    mention_count: count(mentioned_in)
  }
}
```
*(在得到 `all_orgs` 列表后，可以在 Python 代码中按 `mention_count` 排序过滤)*

### 5.2 查询某个国家/实体近期关联的新闻 (国家或公司)
比如查询“伊朗”或“NVIDIA”最近关联的新闻（按事件日期倒序排列，取前 10 条）：
```graphql
{
  # 也可以将 name 换成具体的公司名或国家名
  find_entity(func: eq(name, "伊朗")) {
    name
    dgraph.type
    recent_news: mentioned_in(orderdesc: event_date, first: 10) {
      title
      summary
      category
      event_date
    }
  }
}
```
