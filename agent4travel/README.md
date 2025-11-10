# AI 旅行规划师

一个基于 AI 的智能旅行规划 Web 应用程序，支持语音和文本输入，自动生成详细行程并在地图上展示。

## 功能特性

- 🎯 **智能行程规划**：通过自然语言描述（文本或语音）自动生成详细的旅行计划
- 🗺️ **地图可视化**：在地图上展示所有行程地点，支持交互式浏览
- 💰 **费用管理**：智能记录和分析旅行开销
- 🎤 **语音输入**：支持浏览器语音识别，方便快速输入
- 🌐 **公开访问**：无需登录，所有用户共享行程数据

## 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **Supabase** - 后端即服务（BaaS），提供数据库存储
- **高德地图 API** - 地理编码和地图服务
- **LLM API** - 支持 OpenAI 或阿里云百炼

### 前端
- **React** - 用户界面库
- **Vite** - 快速的前端构建工具
- **TailwindCSS** - 实用优先的 CSS 框架
- **React Router** - 客户端路由
- **高德地图 JS API** - 地图展示

## 项目结构

```
agent4travel/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务逻辑服务
│   ├── requirements.txt    # Python 依赖
│   ├── Dockerfile          # Docker 配置
│   └── env.example         # 环境变量示例
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── pages/          # 页面组件
│   │   ├── context/        # 上下文（已移除认证相关代码）
│   │   └── lib/            # 工具库
│   ├── package.json        # Node.js 依赖
│   └── env.example         # 环境变量示例
├── database.sql            # 数据库表结构
└── README.md              # 项目文档
```

## 快速开始

### 前置要求

1. **Python 3.11+**
2. **Node.js 18+**
3. **Supabase 账户** - 用于数据库存储（无需认证功能）
4. **高德地图 API Key** - 用于地图服务
5. **LLM API Key** - OpenAI 或阿里云百炼

### 1. 数据库设置

1. 在 Supabase 创建新项目
2. 在 SQL 编辑器中执行 `database.sql` 文件中的 SQL 语句
   - **注意**：数据库表已移除用户认证，所有数据对所有用户开放
   - RLS（行级安全）已禁用，允许公开访问
3. 获取 Supabase URL 和 Service Role Key（仅用于后端数据访问）

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp env.example .env

# 编辑 .env 文件，填入您的 API Keys
# SUPABASE_URL=...
# SUPABASE_SERVICE_KEY=...
# OPENAI_API_KEY=... 或 BAILIAN_API_KEY=...
# GAODE_WEB_API_KEY=...
```

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 复制环境变量文件
cp env.example .env

# 编辑 .env 文件，填入您的 API Keys
# 注意：前端不需要 Supabase 配置（无需用户认证）
# VITE_GAODE_JS_API_KEY=...
# VITE_API_BASE_URL=http://localhost:8000
```

### 4. 运行开发服务器

**后端：**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端：**
```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 查看应用。

## 环境变量配置

### 后端 (.env)

```ini
# Supabase
SUPABASE_URL="https://[YOUR_PROJECT_ID].supabase.co"
SUPABASE_SERVICE_KEY="[YOUR_SERVICE_ROLE_KEY]"

# LLM API (二选一)
OPENAI_API_KEY="[YOUR_OPENAI_API_KEY]"
OPENAI_BASE_URL="https://api.openai.com/v1"
LLM_PROVIDER="openai"

# 或
# BAILIAN_API_KEY="[YOUR_BAILIAN_API_KEY]"
# LLM_PROVIDER="bailian"

# 高德地图
GAODE_WEB_API_KEY="[YOUR_GAODE_WEB_API_KEY]"
```

### 前端 (.env)

```ini
# 高德地图
VITE_GAODE_JS_API_KEY="[YOUR_GAODE_JS_API_KEY]"

# API 地址（开发环境）
VITE_API_BASE_URL="http://localhost:8000"

# 注意：此项目为公开访问，无需用户认证
# Supabase 仅在后端用于数据存储，前端不需要 Supabase 配置
```

## API 文档

后端 API 文档可在运行后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API 端点

**所有 API 端点均为公开访问，无需认证**

- `POST /api/v1/trips/plan` - 创建旅行计划
- `GET /api/v1/trips` - 获取所有旅行计划（所有用户共享）
- `GET /api/v1/trips/{trip_id}` - 获取旅行计划详情
- `POST /api/v1/trips/expense` - 创建费用记录

## Docker 部署

### 构建 Docker 镜像

```bash
# 在项目根目录 (agent4travel/) 执行
docker build -t ai-travel-planner .
```

### 运行 Docker 容器

```bash
# 确保 backend/.env 文件存在并配置正确
docker run -p 8000:8000 --env-file backend/.env ai-travel-planner
```

注意：
- Dockerfile 使用多阶段构建，会自动构建前端并将静态文件复制到后端
- 确保 `backend/.env` 文件中包含所有必要的环境变量
- 容器启动后，访问 http://localhost:8000 即可使用应用

## 使用说明

### 创建旅行计划

1. 打开网站，直接进入 Dashboard（无需登录）
2. 在输入框中输入您的旅行需求，例如：
   - "我想去日本，5天，预算1万元，喜欢美食和动漫"
   - "计划去北京旅游3天，预算5000元"
3. 也可以点击麦克风按钮使用语音输入
4. 点击"生成行程"按钮，AI 将自动生成详细的旅行计划
5. **注意**：所有生成的行程对所有用户可见，所有人都可以查看和使用

### 查看行程详情

1. 在 Dashboard 点击任意行程卡片
2. 左侧显示详细的行程时间线
3. 右侧显示地图，所有地点都会标记在地图上
4. 鼠标悬停在左侧活动上，地图会自动定位到对应位置

### 记录费用

1. 在行程详情页底部找到"费用记录"区域
2. 输入费用描述，例如："拉面 50 元"
3. AI 会自动解析金额和类别
4. 也可以使用语音输入记录费用

## 开发指南

### 添加新的 LLM 提供商

1. 在 `backend/app/services/llm_service.py` 中添加新的提供商支持
2. 在 `backend/app/core/config.py` 中添加相应的环境变量
3. 更新 `LLM_PROVIDER` 环境变量

### 自定义样式

前端使用 TailwindCSS，可以在 `tailwind.config.js` 中自定义主题。

## 常见问题

### 1. 语音识别不工作？

确保使用支持 Web Speech API 的浏览器（Chrome、Edge 等），并且允许浏览器访问麦克风权限。

### 2. 地图不显示？

检查高德地图 JS API Key 是否正确配置，并确保网络连接正常。

### 3. LLM API 调用失败？

检查 API Key 是否正确，以及是否有足够的 API 额度。

### 4. 数据库访问权限问题？

确保在 Supabase 中已禁用 RLS（行级安全），允许公开访问。执行 `database.sql` 中的 `ALTER TABLE ... DISABLE ROW LEVEL SECURITY` 语句。

### 5. API 请求返回 404 错误？

**问题症状：** 前端请求 API 时返回 404，后端日志显示请求路径为 `/v1/trips` 而不是 `/api/v1/trips`。

**解决方案：**

1. **检查前端环境变量：**
   - 确保 `frontend/.env` 文件不存在，或者如果存在，确保 `VITE_API_BASE_URL` 设置为 `/api` 或 `http://localhost:8000/api`
   - **不要设置** `VITE_API_BASE_URL="http://localhost:8000"`（缺少 `/api` 前缀）

2. **检查前端 API 客户端：**
   - 打开浏览器开发者工具，查看控制台中的 `[API Client]` 日志
   - 确认 baseURL 包含 `/api` 前缀
   - 确认完整请求路径为 `/api/v1/trips`

3. **检查 Vite 代理配置：**
   - 确保 `frontend/vite.config.js` 中的代理配置正确
   - 重启前端开发服务器：`npm run dev`

4. **验证后端路由：**
   - 访问 http://localhost:8000/docs 查看 API 文档
   - 确认路由为 `/api/v1/trips` 而不是 `/v1/trips`

5. **测试 API：**
   ```bash
   # 测试获取行程列表
   curl http://localhost:8000/api/v1/trips
   
   # 测试创建行程
   curl -X POST http://localhost:8000/api/v1/trips/plan \
     -H "Content-Type: application/json" \
     -d '{"prompt":"我想去日本，5天，预算1万元"}'
   ```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。

