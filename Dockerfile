# FROM python:3.12-slim

# WORKDIR /app/OpenManus

# RUN apt-get update && apt-get install -y --no-install-recommends git curl \
#     && rm -rf /var/lib/apt/lists/* \
#     && (command -v uv >/dev/null 2>&1 || pip install --no-cache-dir uv)

# COPY . .

# RUN uv pip install --system -r requirements.txt

# CMD ["bash"]
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（Playwright 需要）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install chromium --with-deps

# 复制项目代码
COPY . .

# 启动服务（使用环境变量 PORT）
CMD ["sh", "-c", "uvicorn web_api:app --host 0.0.0.0 --port ${PORT:-8000}"]
