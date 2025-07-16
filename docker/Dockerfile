FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 1. 安装 uv 到系统 Python（不创建虚拟环境）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir uv==0.7.13


# 2. 使用 uv 创建和管理虚拟环境
RUN uv venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/.venv"

# 3. 复制依赖文件
COPY . .

# 4. 使用虚拟环境中的 uv 安装依赖
RUN uv sync

# 5. 安装需要编译的依赖
RUN pip install --no-cache-dir psycopg2-binary==2.9.9 sqlalchemy==2.0.30

# 6. 设置工作目录
WORKDIR /app

# 7. 复制应用代码
# COPY . .

# 8. 启动命令
CMD ["/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]