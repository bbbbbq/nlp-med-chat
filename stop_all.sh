#!/bin/bash

# 医疗AI聊天应用一键停止脚本
# 停止所有相关服务和容器

echo "=========================================="
echo "🛑 医疗AI聊天应用一键停止脚本"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 成功信息函数
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 信息输出函数
info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 警告信息函数
warn_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
info_msg "开始停止医疗AI聊天应用的所有服务..."
echo ""

# 1. 停止前端服务 (端口5173)
echo "=========================================="
info_msg "步骤 1/4: 停止前端服务"
echo "=========================================="

if lsof -i :5173 -t >/dev/null 2>&1; then
    info_msg "正在停止前端服务 (端口5173)..."
    lsof -i :5173 | awk 'NR!=1 {print $2}' | xargs kill -9 2>/dev/null
    success_msg "前端服务已停止"
else
    info_msg "前端服务未运行"
fi

# 2. 停止后端服务 (端口3000)
echo ""
echo "=========================================="
info_msg "步骤 2/4: 停止后端服务"
echo "=========================================="

if lsof -i :3000 -t >/dev/null 2>&1; then
    info_msg "正在停止后端服务 (端口3000)..."
    lsof -i :3000 | awk 'NR!=1 {print $2}' | xargs kill -9 2>/dev/null
    success_msg "后端服务已停止"
else
    info_msg "后端服务未运行"
fi

# 3. 停止 MySQL 容器
echo ""
echo "=========================================="
info_msg "步骤 3/4: 停止 MySQL 数据库服务"
echo "=========================================="

if [ -d "mysql" ]; then
    cd mysql
    if [ -f "docker-compose.yml" ]; then
        info_msg "正在停止 MySQL 容器..."
        sudo docker-compose down 2>/dev/null
        success_msg "MySQL 服务已停止"
    else
        warn_msg "MySQL docker-compose.yml 文件不存在"
    fi
    cd "$SCRIPT_DIR"
else
    warn_msg "MySQL 目录不存在"
fi

# 4. 停止 MinIO 容器
echo ""
echo "=========================================="
info_msg "步骤 4/4: 停止 MinIO 存储服务"
echo "=========================================="

if [ -d "minio" ]; then
    cd minio
    if [ -f "docker-compose.yml" ]; then
        info_msg "正在停止 MinIO 容器..."
        sudo docker-compose down 2>/dev/null
        success_msg "MinIO 服务已停止"
    else
        warn_msg "MinIO docker-compose.yml 文件不存在"
    fi
    cd "$SCRIPT_DIR"
else
    warn_msg "MinIO 目录不存在"
fi

# 5. 清理可能残留的进程
echo ""
echo "=========================================="
info_msg "清理残留进程"
echo "=========================================="

# 查找并停止可能的Node.js进程
NODE_PROCESSES=$(pgrep -f "node.*dev\|npm.*dev" 2>/dev/null)
if [ ! -z "$NODE_PROCESSES" ]; then
    info_msg "正在清理Node.js开发服务进程..."
    echo "$NODE_PROCESSES" | xargs kill -9 2>/dev/null
    success_msg "Node.js进程已清理"
fi

# 查找并停止可能的Python进程
PYTHON_PROCESSES=$(pgrep -f "python.*app.py\|uvicorn\|gunicorn" 2>/dev/null)
if [ ! -z "$PYTHON_PROCESSES" ]; then
    info_msg "正在清理Python后端服务进程..."
    echo "$PYTHON_PROCESSES" | xargs kill -9 2>/dev/null
    success_msg "Python进程已清理"
fi

echo ""
echo "=========================================="
success_msg "🎉 所有服务已停止！"
echo "=========================================="

echo ""
info_msg "服务状态概览:"
echo "  📦 MinIO 存储服务: 已停止"
echo "  🗄️  MySQL 数据库: 已停止"
echo "  🔧 后端服务: 已停止"
echo "  🌐 前端服务: 已停止"

echo ""
info_msg "如需重新启动服务，请运行: ./start_all.sh"

echo ""
success_msg "停止脚本执行完成！"
