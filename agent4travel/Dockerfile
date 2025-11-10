# 多阶段构建 Dockerfile
# 从项目根目录构建

# 阶段 1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端文件
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# 阶段 2: Python 后端
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 从阶段 1 复制构建好的前端静态文件
COPY --from=frontend-builder /app/frontend/dist ./static

# 暴露端口
EXPOSE 8000

WORKDIR /app/backend
# 相应地，从新的 WORKDIR 启动 uvicorn

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


