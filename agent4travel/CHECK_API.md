# API 路径问题诊断指南

## 问题描述
前端请求 API 时返回 404，后端日志显示请求路径为 `/v1/trips` 而不是 `/api/v1/trips`。

## 快速检查步骤

### 1. 检查前端环境变量

**检查 `frontend/.env` 文件：**

```bash
# 如果文件存在，检查内容
cat frontend/.env
```

**正确的配置：**
- ✅ `VITE_API_BASE_URL=/api` （推荐，使用 Vite 代理）
- ✅ `VITE_API_BASE_URL=http://localhost:8000/api` （直接连接后端）
- ❌ `VITE_API_BASE_URL=http://localhost:8000` （错误！缺少 /api）

**如果文件不存在或配置错误：**
```bash
# 删除或重命名现有的 .env 文件
mv frontend/.env frontend/.env.bak

# 或者创建正确的 .env 文件
echo 'VITE_API_BASE_URL=/api' > frontend/.env
```

### 2. 重启前端开发服务器

```bash
cd frontend
# 停止当前服务器 (Ctrl+C)
# 重新启动
npm run dev
```

### 3. 检查浏览器控制台

打开浏览器开发者工具（F12），查看控制台输出：

**应该看到：**
```
[API Client] baseURL: /api
[API Client] 完整请求路径示例: /api/v1/trips
[API Request] GET /v1/trips
[API Request] Full URL: /api/v1/trips
```

**如果看到错误的 baseURL（比如 `http://localhost:8000`），说明环境变量配置错误。**

### 4. 验证后端路由

访问 http://localhost:8000/docs 查看 API 文档，确认路由为：
- ✅ `/api/v1/trips`
- ✅ `/api/v1/trips/{trip_id}`
- ✅ `/api/v1/trips/plan`
- ✅ `/api/v1/trips/expense`

### 5. 手动测试 API

```bash
# 测试获取行程列表
curl http://localhost:8000/api/v1/trips

# 如果返回数据或空数组，说明后端路由正常
# 如果返回 404，说明后端路由配置有问题
```

## 常见问题解决

### 问题 1: 前端 .env 文件设置了错误的 baseURL

**解决方案：**
1. 删除或修改 `frontend/.env` 文件
2. 确保 `VITE_API_BASE_URL=/api` 或 `VITE_API_BASE_URL=http://localhost:8000/api`
3. 重启前端开发服务器

### 问题 2: Vite 代理没有工作

**解决方案：**
1. 检查 `frontend/vite.config.js` 中的代理配置
2. 确保后端运行在 `http://localhost:8000`
3. 重启前端开发服务器

### 问题 3: 后端路由没有正确注册

**解决方案：**
1. 检查 `backend/app/main.py` 中的路由注册
2. 确认 `app.include_router(trips.router, prefix="/api/v1")`
3. 重启后端服务器

## 修复后的验证

修复后，应该看到：

1. **浏览器控制台：**
   - baseURL 包含 `/api`
   - 完整请求路径为 `/api/v1/trips`

2. **后端日志：**
   - 请求路径为 `/api/v1/trips`（不是 `/v1/trips`）
   - 返回 200 状态码（不是 404）

3. **前端功能：**
   - 可以正常加载行程列表
   - 可以正常创建新行程

