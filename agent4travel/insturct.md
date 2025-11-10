## AI 旅行规划师：实现设计文档

**致 AI 助手（Cursor / Trae）：**

你好。请你作为首席开发者，根据以下设计文档实现一个完整的 Web 应用程序。你的任务是编写所有代码，包括后端、前端、数据库配置和 Dockerfile。

本项目的设计目标是**简单、实用、易于维护**。请严格遵循本文档中定义的 API、数据库模式和文件结构。

### 一、项目概述

**目标：** 创建一个 AI 驱动的旅行规划 Web 应用。
**核心功能：**

1.  **智能规划：** 用户通过语音或文本输入（例如：“我想去日本，5 天，预算 1 万元，喜欢美食和动漫”）获取详细的每日行程。
2.  **费用管理：** 用户可以通过语音或文本记录开销，AI 自动进行预算分析。
3.  **用户系统：** 用户可以注册/登录，保存和管理他们的旅行计划。

### 二、技术栈

  * **前端：** React (Vite) + TailwindCSS
  * **后端：** Python (FastAPI)
  * **数据库/认证：** Supabase
  * **地图：** 高德地图 (GaoDe)
  * **语音识别：** 浏览器 Web Speech API (无需 Key)
  * **AI (LLM)：** 待定 (由用户在 `.env` 中提供 Key)

### 三、API Key 管理 (重要！)

此项目需要多个 API Key。你必须将所有 Key 的配置**外部化**。

1.  **创建 `.env.example` 文件：** 在 `backend/` 和 `frontend/` 目录中创建 `.env.example` 文件。
2.  **编码实现：**
      * **后端：** 使用 Pydantic Settings (或 `python-dotenv`) 从环境变量中读取配置。
      * **前端：** 使用 Vite 的 `import.meta.env.VITE_...` 方式读取环境变量。
3.  \*\*最终用户（我）\*\*将复制这些 `.env.example` 文件为 `.env` 并填入他们自己的 Key。

**`backend/.env.example`**

```ini
# --- Supabase (后端服务角色) ---
SUPABASE_URL="https://[YOUR_PROJECT_ID].supabase.co"
SUPABASE_SERVICE_KEY="[YOUR_SUPABASE_SERVICE_ROLE_KEY]"

# --- LLM API (用户自选) ---
# (例如，如果用阿里云百炼)
BAILIAN_API_KEY="[YOUR_BAILIAN_API_KEY]"
# (或者用 OpenAI)
# OPENAI_API_KEY="[YOUR_OPENAI_API_KEY]"

# --- 高德地图 (后端 Web 服务 API，用于地理编码) ---
GAODE_WEB_API_KEY="[YOUR_GAODE_WEB_SERVICE_API_KEY]"
```

**`frontend/.env.example`**

```ini
# --- Supabase (前端 'anon' public key) ---
VITE_SUPABASE_URL="https://[YOUR_PROJECT_ID].supabase.co"
VITE_SUPABASE_ANON_KEY="[YOUR_SUPABASE_ANON_PUBLIC_KEY]"

# --- 高德地图 (前端 JS API) ---
VITE_GAODE_JS_API_KEY="[YOUR_GAODE_JS_API_KEY]"
```

### 四、项目文件结构

请按以下结构组织项目（Monorepo）：

```
/ai-travel-planner/
├── /backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI 应用程序实例和中间件
│   │   ├── api/            # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trips.py        # 行程规划路由
│   │   │   │   └── users.py        # 用户/认证路由
│   │   ├── core/           # 核心配置
│   │   │   └── config.py   # Pydantic Settings，用于读取 .env
│   │   ├── models/         # Pydantic 模型
│   │   │   └── schema.py
│   │   └── services/       # 业务逻辑
│   │       ├── llm_service.py # 封装 LLM 调用
│   │       ├── map_service.py # 封装高德地图调用
│   │       └── auth_service.py # 封装 Supabase 认证
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
└── /frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Map.jsx
    │   │   ├── VoiceInput.jsx
    │   │   ├── ItineraryTimeline.jsx
    │   │   └── Navbar.jsx
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── Dashboard.jsx        # 所有行程列表
    │   │   └── TripDetail.jsx       # 单个行程详情 (地图+时间线)
    │   ├── context/
    │   │   └── AuthContext.jsx      # 全局用户状态
    │   ├── lib/
    │   │   ├── supabaseClient.js    # Supabase 客户端实例
    │   │   └── apiClient.js         # Axios/Fetch 实例 (用于调用后端)
    │   ├── App.jsx
    │   └── main.jsx
    ├── .env.example
    ├── index.html
    └── package.json
```

-----

### 五、后端实现 (FastAPI)

#### 1\. 数据库模式 (Supabase Postgres)

请在 Supabase 的 SQL 编辑器中执行以下 DDL 来创建表。

```sql
-- 1. 旅行计划 (trips)
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    destination TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    budget NUMERIC,
    preferences TEXT, -- 存储 "美食, 动漫" 等
    raw_prompt TEXT,  -- 存储用户原始输入
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 每日行程 (itineraries)
CREATE TABLE itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE NOT NULL,
    day_number INT NOT NULL,
    title TEXT,
    summary TEXT,
    activities JSONB, -- 存储 [{ "time": "09:00", "activity": "...", "location_name": "...", "lat": 12.34, "lng": 56.78 }]
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. 费用记录 (expenses)
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    category TEXT, -- 例如: 餐饮, 交通, 住宿
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. 启用 RLS (Row Level Security)
-- 确保用户只能访问自己的数据
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User can manage their own trips" ON trips
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User can manage their own itineraries" ON itineraries
    FOR ALL USING (EXISTS (SELECT 1 FROM trips WHERE trips.id = itineraries.trip_id AND trips.user_id = auth.uid()));
CREATE POLICY "User can manage their own expenses" ON expenses
    FOR ALL USING (auth.uid() = user_id);
```

#### 2\. Pydantic 模型 (`backend/app/models/schema.py`)

你需要为 API 请求和响应定义清晰的模型。

```python
from pydantic import BaseModel
from typing import List, Optional, Any

# --- 用户/认证 ---
class UserCreate(BaseModel):
    email: str
    password: str

# --- 核心：行程规划 ---
class PlanRequest(BaseModel):
    # 接收用户的原始自然语言输入
    prompt: str  # "我想去日本，5 天，预算 1 万元，喜欢美食和动漫"

class Activity(BaseModel):
    time: str     # "09:00"
    activity: str # "参观秋叶原"
    description: Optional[str]
    location_name: str # "秋叶原电器街"
    lat: Optional[float]
    lng: Optional[float]

class DailyItinerary(BaseModel):
    day: int
    title: str    # "第一天：动漫圣地巡礼"
    summary: str
    activities: List[Activity]

class TripPlanResponse(BaseModel):
    trip_id: Any # UUID
    destination: str
    daily_plan: List[DailyItinerary]
    budget_analysis: str

# --- 费用 ---
class ExpenseCreate(BaseModel):
    trip_id: Any # UUID
    description: str  # 可以是 "拉面 50 元"
    amount: Optional[float]
    category: Optional[str]
```

#### 3\. 后端服务 (`backend/app/services/`)

**`auth_service.py`**

  * 使用 `supabase-python` 库。
  * `get_user_from_token(token: str)`: 验证前端发来的 JWT，并返回 user。FastAPI 将用此作为依赖项 (Dependency) 来保护路由。

**`llm_service.py` (关键逻辑)**

  * `generate_trip_plan(user_prompt: str)`:
    1.  构造一个**高质量的 Prompt**，发送给 `config.py` 中配置的 LLM API。
    2.  **Prompt 要求：**
          * "你是一个旅行规划师。"
          * "根据用户输入：`{user_prompt}`"
          * "**严格**按照以下 JSON 格式返回行程，不要有任何多余的文字。"
          * 提供 JSON 格式示例 (对应 `TripPlanResponse`，但不包含 `lat/lng`)。
    3.  接收 LLM 返回的 JSON 字符串，将其解析为 Pydantic 模型。
  * `extract_expense(expense_text: str)`:
    1.  用于语音记账。输入："拉面 50 元"。
    2.  **Prompt 要求：**
          * "从 `{expense_text}` 中提取开销项目、金额和类别。"
          * "**严格**返回 JSON 格式：`{\"description\": \"拉面\", \"amount\": 50, \"category\": \"餐饮\"}`"
    3.  返回解析后的 JSON。

**`map_service.py`**

  * `get_coordinates(location_name: str)`:
    1.  调用高德 Web 服务 API（`GAODE_WEB_API_KEY`）的地理编码功能。
    2.  输入 "秋叶原电器街"，返回 `{"lat": ..., "lng": ...}`。

#### 4\. API 路由 (`backend/app/api/v1/trips.py`)

  * **`POST /api/v1/trips/plan`** (受保护的)

    1.  接收 `PlanRequest` (含 `prompt`)。
    2.  调用 `llm_service.generate_trip_plan(prompt)`，获取 JSON 格式的行程。
    3.  **循环**遍历行程中的**每一项** `activity`：
          * 调用 `map_service.get_coordinates(activity.location_name)`。
          * 将获取到的 `lat/lng` 填入 `activity` 对象中。
    4.  将完整的行程（含经纬度）存入 Supabase 的 `trips` 和 `itineraries` 表。
    5.  向前端返回 `TripPlanResponse`。

  * **`GET /api/v1/trips`** (受保护的)

      * 从 Supabase 查询 `trips` 表，返回该用户的所有旅行计划列表。

  * **`GET /api/v1/trips/{trip_id}`** (受保护的)

      * 查询 `trips` 和 `itineraries`，返回单个旅行计划的详细信息（用于行程详情页）。

  * **`POST /api/v1/trips/expense`** (受保护的)

    1.  接收 `ExpenseCreate` (含 `description`)。
    2.  **判断：** 如果 `amount` 未提供，则调用 `llm_service.extract_expense(description)` 来解析 `description` (例如 "拉面 50 元")。
    3.  将解析后的 `description`, `amount`, `category` 存入 `expenses` 表。

-----

### 六、前端实现 (React)

#### 1\. 认证 (`AuthContext.jsx` & `supabaseClient.js`)

  * `supabaseClient.js`: 使用 `VITE_SUPABASE_URL` 和 `VITE_SUPABASE_ANON_KEY` 初始化 Supabase 客户端。
  * `AuthContext.jsx`:
      * 提供 `user`, `login(email, pass)`, `register(email, pass)`, `logout()` 方法。
      * 使用 Supabase 的 `onAuthStateChange` 监听器来自动更新全局 `user` 状态。
  * `apiClient.js`:
      * 创建一个 Axios 实例。
      * 添加一个**请求拦截器**，在**每次**请求后端 API (例如 `/api/v1/trips`) 时，自动从 Supabase 获取 `session.access_token` 并将其添加到 `Authorization: Bearer <token>` 头中。

#### 2\. 页面与组件

  * **`Login.jsx` / `Register.jsx`:**

      * 调用 `AuthContext` 中的 `login` / `register` 方法。
      * 登录成功后自动跳转到 `/dashboard`。

  * **`Dashboard.jsx` (主页):**

      * **（核心功能）智能输入框：**
          * 一个大的 `<textarea>` 用于文本输入。
          * 一个 `VoiceInput.jsx` 组件（麦克风按钮）。
          * **`VoiceInput.jsx`:** 使用浏览器 `window.SpeechRecognition` API。点击按钮时开始录音，识别中文 (`lang = 'zh-CN'`)。识别完成后，将结果 `transcript` 填入 `<textarea>`。
      * 用户在 `<textarea>` 中输入（或语音输入）"我想去日本..." 后点击 "生成" 按钮。
      * 点击 "生成"：
        1.  显示加载状态 (Loading spinner)。
        2.  调用 `apiClient.post('/api/v1/trips/plan', { prompt: ... })`。
        3.  请求成功后，`apiClient` 会返回 `TripPlanResponse`。
        4.  使用 `react-router` 的 `useNavigate` 跳转到行程详情页：`Maps('/trip/NEW_TRIP_ID')`。
      * **行程列表：**
          * 调用 `apiClient.get('/api/v1/trips')` 获取历史行程列表并展示。

  * **`TripDetail.jsx` (行程详情页):**

      * 从 URL (`/trip/:tripId`) 获取 `tripId`。
      * 调用 `apiClient.get('/api/v1/trips/{tripId}')` 获取详细行程数据。
      * **布局：** 左右分栏。
      * **左侧：`ItineraryTimeline.jsx`**
          * 使用 Timeline (时间线) 组件 (如 Ant Design 或自制)
          * 按 `day` 渲染 `DailyItinerary`。
          * 展示 `activities` 列表 (时间, 活动名, 地点)。
      * **右侧：`Map.jsx`**
          * 使用 `@amap/amap-jsapi-loader` 加载高德地图 JS API (使用 `VITE_GAODE_JS_API_KEY`)。
          * 将该行程**所有**的 `activities` 的 `lat/lng` 坐标在地图上渲染为标记 (Marker)。
          * (加分项) 当鼠标悬停在左侧的某个 `activity` 上时，地图应平移到对应的 Marker 并高亮。
      * **费用记录模块：**
          * 一个简单的表单 (输入框 "说明"，按钮 "记一笔")。
          * 输入 "拉面 50 元"，点击提交。
          * 调用 `apiClient.post('/api/v1/trips/expense', { trip_id: ..., description: "拉面 50 元" })`。
          * 后端 AI 会自动解析金额。

### 七、部署 (Docker)

请在 `backend/Dockerfile` 中提供一个用于生产的 Dockerfile。

1.  **多阶段构建：**
      * **阶段 1 (Node):** 构建 React 前端 (运行 `npm run build`)。
      * **阶段 2 (Python):** \* 安装 Python 依赖。
          * 复制后端代码。
          * 将阶段 1 构建好的前端静态文件 ( `frontend/dist` ) 复制到后端的一个 `/static` 目录中。
2.  **配置 FastAPI：**
      * 在 `main.py` 中，使用 `StaticFiles` 将 `/static` 目录挂载到根路径 `/`。
      * `app.mount("/", StaticFiles(directory="/static", html=True), name="static")`
3.  **启动命令：** 使用 `uvicorn` 启动 FastAPI。

**最终结果：** 只需运行这一个 Docker 容器，即可同时提供前端 React 页面和后端 API 服务。
