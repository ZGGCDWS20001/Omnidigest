# OmniDigest CI/CD 部署指南

## 概述

本文档描述 OmniDigest 项目的完整 CI/CD 流程：GitHub → Harbor 自动打包 → 服务器容器自动更新。

## 当前架构

```
GitHub (push tag v*)
    ↓
GitHub Actions (CI/CD)
    ↓
Harbor 镜像仓库
    ↓
服务器 (Watchtower/Webhook)
    ↓
Docker 容器自动更新
```

## 现有配置

### CI Workflow (ci.yml)

**触发条件**：
- push 到 master/develop 分支
- PR 到 master/develop 分支

**执行任务**：
1. backend-test：运行后端测试
2. frontend-build：构建前端
3. docker-build：构建 Docker 镜像（本地测试）

### CD Workflow (cd.yml)

**触发条件**：push `v*` 标签（如 v1.0.0）

**执行任务**：
1. 登录 Harbor
2. 构建后端镜像 → 推送到 `harbor.franklinworksite.top/public/omnidigest:${VERSION}` 和 `latest`
3. 构建前端镜像 → 推送到 `harbor.franklinworksite.top/public/omnidigest-frontend:${VERSION}` 和 `latest`

## 自动部署方案

### 方案 1: Watchtower（推荐）

Watchtower 是一个后台进程，监控指定容器使用的镜像更新并自动拉取更新。

**安装命令**：

```bash
# 方式 1: 每天凌晨 3 点定时检查更新（推荐）
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --schedule "0 3 * * *" \
  --cleanup \
  --include-stopped \
  --revive-stopped \
  omnidigest omnidigest-frontend

# 方式 2: 持续监控（每 5 分钟检查）
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WATCHTOWER_CLEANUP=true \
  -e WATCHTOWER_TIMEOUT=60s \
  -e WATCHTOWER_POLL_INTERVAL=300 \
  containrrr/watchtower \
  --include-stopped \
  --revive-stopped \
  omnidigest omnidigest-frontend
```

**Watchtower 参数说明**：
- `--schedule "0 3 * * *"`：每天凌晨 3 点执行
- `--cleanup`：更新后删除旧镜像
- `--include-stopped`：也检查已停止的容器
- `--revive-stopped`：自动重启已停止的容器

**管理命令**：

```bash
# 查看 Watchtower 日志
docker logs watchtower

# 查看可用的更新
docker run --rm containrrr/watchtower --help

# 手动触发更新（不常用）
docker kill -s USR1 watchtower
```

### 方案 2: Webhook

Webhook 可以实现 GitHub 推送镜像后立即触发服务器更新。

#### 步骤 1: 服务器安装 webhook

```bash
# Ubuntu/Debian
sudo apt install webhook -y

# 或使用 Docker 运行
docker run -d \
  --name webhook \
  -p 9000:9000 \
  -v /home/frank/hooks:/etc/webhook \
  alpine:latest \
  apk add --no-cache webhook && \
  webhook -hooks /etc/webhook/hooks.yaml -verbose
```

#### 步骤 2: 创建部署脚本

`/home/frank/hooks/redeploy.sh`:
```bash
#!/bin/bash
set -e

cd /home/frank/Documents/code/newssync-main

# 拉取最新镜像并重启容器
docker-compose pull
docker-compose up -d

echo "Deployment completed at $(date)"
```

#### 步骤 3: 配置 Webhook

`/etc/webhook/hooks.yaml`:
```yaml
- id: redeploy-omnidigest
  execute-command: "/home/frank/hooks/redeploy.sh"
  command-working-directory: "/home/frank/Documents/code/newssync-main"
  trigger-response-pair: "Redeploy triggered"
```

#### 步骤 4: 修改 docker-compose.yml

修改服务配置，使用镜像而非 build：

```yaml
services:
  omnidigest:
    image: harbor.franklinworksite.top/public/omnidigest:latest
    pull_policy: always
    # 移除 build: 部分
    # ...

  frontend:
    image: harbor.franklinworksite.top/public/omnidigest-frontend:latest
    pull_policy: always
    # ...
```

#### 步骤 5: 修改 GitHub Actions (cd.yml)

在推送镜像后添加 webhook 调用：

```yaml
      - name: Trigger server update
        if: success()
        run: |
          curl -X POST https://your-server.com:9000/hooks/redeploy-omnidigest
```

## 发布流程

1. **开发完成**，合并到 master 分支

2. **打标签发布**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **GitHub Actions 自动执行**：
   - 构建镜像
   - 推送到 Harbor
   - 触发服务器更新（如果使用 Webhook 方案）

4. **Watchtower 自动更新**（如果使用 Watchtower 方案）：
   - 定时检查镜像更新
   - 自动拉取并重启容器

## 镜像版本管理

| 标签 | 说明 | 更新时机 |
|------|------|----------|
| `latest` | 最新稳定版 | 每次发布 |
| `v1.0.0` | 语义化版本 | 特定版本 |
| `v1.0` | 大版本 | 每次小版本更新 |

## 故障排查

### 查看容器状态
```bash
docker-compose ps
docker-compose logs -f omnidigest
```

### 查看 Watchtower 日志
```bash
docker logs watchtower
```

### 手动回滚
```bash
# 查看可用镜像版本
docker images | grep omnidigest

# 手动拉取指定版本
docker pull harbor.franklinworksite.top/public/omnidigest:v1.0.0

# 重启容器
docker-compose up -d
```

### Webhook 未触发
```bash
# 检查 webhook 服务状态
docker logs webhook

# 测试 webhook 端点
curl -v https://your-server.com:9000/hooks/redeploy-omnidigest
```

## 安全考虑

1. **Harbor 凭证**：存储在 GitHub Secrets 中
   - `HARBOR_USERNAME`
   - `HARBOR_PASSWORD`

2. **Webhook 安全**：
   - 使用 HTTPS
   - 配置 IP 白名单
   - 使用 webhook secret

3. **镜像签名**：可选配置 Docker Content Trust

## 相关文件

- `.github/workflows/ci.yml` - CI 配置
- `.github/workflows/cd.yml` - CD 配置
- `docker-compose.yml` - 容器编排
- `backend/Dockerfile` - 后端镜像
- `frontend/Dockerfile` - 前端镜像
