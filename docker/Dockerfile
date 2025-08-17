FROM python:3.12-slim

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    supervisor && \
    rm -rf /var/lib/apt/lists/*


RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir uv==0.7.13

RUN uv venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/.venv"

COPY . .

RUN uv sync

RUN pip install --no-cache-dir psycopg2-binary==2.9.9 sqlalchemy==2.0.30

WORKDIR /app

CMD ["/app/start_services.sh", "start"]
