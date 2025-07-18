#!/bin/bash

# 医疗AI聊天应用一键启动脚本
# 按照依赖关系顺序启动所有服务

echo "==========================================="
echo "🚀 医疗AI聊天应用一键启动脚本"
echo "==========================================="

# 检查Docker服务状态
check_docker_service() {
    if ! sudo systemctl is-active --quiet docker; then
        warn_msg "Docker服务未运行，正在启动..."
        sudo systemctl start docker
        sleep 3
    fi
    if ! sudo docker ps >/dev/null 2>&1; then
        handle_error "Docker服务无法正常运行，请检查Docker安装"
    fi
    return 0
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
handle_error() {
    echo -e "${RED}❌ 错误: $1${NC}"
    echo "启动过程中断，请检查错误信息"
    exit 1
}

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

# 检查目录是否存在
check_directory() {
    if [ ! -d "$1" ]; then
        handle_error "目录 $1 不存在"
    fi
}

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        handle_error "文件 $1 不存在"
    fi
}

echo ""
info_msg "开始启动医疗AI聊天应用的所有服务..."
echo ""

# 检查Docker服务
info_msg "检查Docker服务状态..."
check_docker_service
success_msg "Docker服务正常运行"
echo ""

# 1. 启动 MinIO 存储服务
echo "=========================================="
info_msg "步骤 1/4: 启动 MinIO 存储服务"
echo "=========================================="

check_directory "minio"
check_file "minio/start.sh"

cd minio
info_msg "正在启动 MinIO 服务..."
if bash start.sh; then
    success_msg "MinIO 服务启动成功"
else
    handle_error "MinIO 服务启动失败"
fi
cd "$SCRIPT_DIR"

echo ""

# 2. 启动 MySQL 数据库服务
echo "=========================================="
info_msg "步骤 2/4: 启动 MySQL 数据库服务"
echo "=========================================="

check_directory "mysql"
check_file "mysql/start.sh"

cd mysql
info_msg "正在启动 MySQL 服务..."
if bash start.sh; then
    success_msg "MySQL 服务启动成功"
else
    handle_error "MySQL 服务启动失败"
fi
cd "$SCRIPT_DIR"

echo ""

# 等待数据库服务完全启动
info_msg "等待数据库服务完全启动..."
sleep 10

# 3. 启动后端服务
echo "=========================================="
info_msg "步骤 3/4: 启动后端服务"
echo "=========================================="

check_directory "bach_end"
check_file "bach_end/start.sh"

cd bach_end
info_msg "正在启动后端服务..."
# 后端服务在后台启动
bash start.sh &
BACKEND_PID=$!
if [ $? -eq 0 ]; then
    success_msg "后端服务启动中..."
    info_msg "后端服务进程ID: $BACKEND_PID"
else
    handle_error "后端服务启动失败"
fi
cd "$SCRIPT_DIR"

echo ""

# 等待后端服务启动
info_msg "等待后端服务完全启动..."
sleep 15

# 4. 启动前端服务
echo "=========================================="
info_msg "步骤 4/4: 启动前端服务"
echo "=========================================="

check_directory "nlpchat-front"
check_file "nlpchat-front/start.sh"

cd nlpchat-front
info_msg "正在启动前端服务..."
# 前端服务在后台启动
bash start.sh &
FRONTEND_PID=$!
if [ $? -eq 0 ]; then
    success_msg "前端服务启动中..."
    info_msg "前端服务进程ID: $FRONTEND_PID"
else
    handle_error "前端服务启动失败"
fi
cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
success_msg "🎉 所有服务启动完成！"
echo "=========================================="

echo ""
info_msg "服务状态概览:"
echo "  📦 MinIO 存储服务: 已启动 (Docker容器)"
echo "  🗄️  MySQL 数据库: 已启动 (Docker容器)"
echo "  🔧 后端服务: 启动中 (PID: $BACKEND_PID)"
echo "  🌐 前端服务: 启动中 (PID: $FRONTEND_PID)"

echo ""
info_msg "访问地址:"
echo "  🌐 前端应用: http://localhost:5173"
echo "  🔧 后端API: http://localhost:3000"
echo "  📦 MinIO控制台: http://localhost:9001"

echo ""
warn_msg "注意事项:"
echo "  • 前端和后端服务需要几分钟时间完全启动"
echo "  • 如需停止服务，请使用 Ctrl+C 或运行 stop_all.sh"
echo "  • 查看服务日志请检查各自目录下的日志文件"

echo ""
info_msg "等待前端服务完全启动..."
echo "请稍候，前端服务正在编译和启动中..."

# 等待用户按键退出或保持运行
echo ""
echo "按 Ctrl+C 停止所有服务，或按任意键退出脚本（服务将继续运行）"
read -n 1 -s

echo ""
success_msg "启动脚本执行完成！服务将继续在后台运行。"
