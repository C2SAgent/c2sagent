#!/bin/bash

# 多服务启动脚本
# 用法: ./start_services.sh [start|stop|restart|status]

# 服务配置
APP_NAME="C2SAgent"
APP_DIR="/root/ChenXAn/project_c2sagent/c2sagent/"  # 修改为你的应用目录
VENV_PATH="$APP_DIR/.venv/bin/activate"  # 修改为你的虚拟环境路径

# PID文件位置
PID_DIR="/var/run/$APP_NAME"
FASTAPI_PID="$PID_DIR/fastapi.pid"
A2A_PID="$PID_DIR/a2a.pid"
MCP_PID="$PID_DIR/mcp.pid"

# 确保日志目录存在
LOG_DIR="/var/log/$APP_NAME"
mkdir -p $LOG_DIR
chown -R $USER:$USER $LOG_DIR
chmod -R 755 $LOG_DIR

# PID文件位置
PID_DIR="/var/run/$APP_NAME"
mkdir -p $PID_DIR
chown -R $USER:$USER $PID_DIR
chmod -R 755 $PID_DIR

FASTAPI_PID="$PID_DIR/fastapi.pid"
A2A_PID="$PID_DIR/a2a.pid"
MCP_PID="$PID_DIR/mcp.pid"

# 日志文件位置
FASTAPI_LOG="$LOG_DIR/fastapi.log"
A2A_LOG="$LOG_DIR/a2a.log"
MCP_LOG="$LOG_DIR/mcp.log"

# 启动FastAPI服务
start_fastapi() {
    echo "Starting FastAPI service..."
    cd $APP_DIR
    source $VENV_PATH

    # 先停止可能存在的旧进程
    if [ -f $FASTAPI_PID ]; then
        kill $(cat $FASTAPI_PID) 2>/dev/null
        rm -f $FASTAPI_PID
    fi

    # 启动服务并记录PID
    nohup uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --log-level debug > $FASTAPI_LOG 2>&1 &
    echo $! > $FASTAPI_PID

    sleep 2
    if ps -p $(cat $FASTAPI_PID) > /dev/null; then
        echo "FastAPI service started (PID: $(cat $FASTAPI_PID))"
        echo "Logs: $FASTAPI_LOG"
    else
        echo "Failed to start FastAPI service"
        echo "Check logs: $FASTAPI_LOG"
        return 1
    fi
}

# 启动A2A服务
start_a2a() {
    echo "Starting A2A service..."
    cd $APP_DIR
    source $VENV_PATH
    nohup python -c "from src_a2a.a2a_server import main; main()" > $A2A_LOG 2>&1 &
    echo $! > $A2A_PID
    echo "A2A service started"
}

# 启动MCP服务
start_mcp() {
    echo "Starting MCP service..."
    cd $APP_DIR
    source $VENV_PATH
    nohup python -c "from src_mcp.mcp_server.server.mcp_server import main; main()" > $MCP_LOG 2>&1 &
    echo $! > $MCP_PID
    echo "MCP service started"
}

# 停止服务
stop_service() {
    local service_name=$1
    local pid_file=$2

    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        echo "Stopping $service_name service (PID: $pid)..."
        kill $pid
        rm -f $pid_file
        echo "$service_name service stopped"
    else
        echo "$service_name service is not running"
    fi
}

# 检查服务状态
check_status() {
    local service_name=$1
    local pid_file=$2

    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        if ps -p $pid > /dev/null; then
            echo "$service_name service is running (PID: $pid)"
        else
            echo "$service_name service is not running (stale PID file)"
            rm -f $pid_file
        fi
    else
        echo "$service_name service is not running"
    fi
}

# 主控制逻辑
case "$1" in
    start)
        start_fastapi
        start_a2a
        start_mcp
        ;;
    stop)
        stop_service "FastAPI" $FASTAPI_PID
        stop_service "A2A" $A2A_PID
        stop_service "MCP" $MCP_PID
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        check_status "FastAPI" $FASTAPI_PID
        check_status "A2A" $A2A_PID
        check_status "MCP" $MCP_PID
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

exit 0
