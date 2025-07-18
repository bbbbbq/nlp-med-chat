#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志功能的脚本
验证日志系统是否正常工作，包括文件日志和控制台输出
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger_config import (
    log_info, log_error, log_warning, log_debug,
    log_api_call, log_rag_operation, log_user_interaction
)
from chat import SymptomExtractor

def test_basic_logging():
    """测试基本日志功能"""
    print("🧪 测试基本日志功能...")
    
    # 测试不同级别的日志
    log_info("这是一条信息日志")
    log_warning("这是一条警告日志")
    log_error("这是一条错误日志")
    log_debug("这是一条调试日志")
    
    print("✅ 基本日志测试完成")

def test_api_logging():
    """测试API调用日志"""
    print("🧪 测试API调用日志...")
    
    # 模拟API调用日志
    log_api_call("POST", "https://api.deepseek.com/chat/completions", 200, 1.5)
    log_api_call("POST", "https://api.deepseek.com/chat/completions", 429, 0.8, "Rate limit exceeded")
    
    print("✅ API调用日志测试完成")

def test_rag_logging():
    """测试RAG操作日志"""
    print("🧪 测试RAG操作日志...")
    
    # 模拟RAG操作日志
    log_rag_operation("知识检索", "头痛、发热、咳嗽", 0.85, 3)
    log_rag_operation("RAG增强诊断", "匹配度超过阈值", 0.85)
    log_rag_operation("传统诊断", "匹配度未达阈值", 0.65)
    
    print("✅ RAG操作日志测试完成")

def test_user_interaction_logging():
    """测试用户交互日志"""
    print("🧪 测试用户交互日志...")
    
    # 模拟用户交互日志
    log_user_interaction("医疗影像分析", "提示词长度: 50字符")
    log_user_interaction("聊天请求", "IP: 127.0.0.1, Content-Type: multipart/form-data")
    log_user_interaction("病例生成", "包含2张影像文件")
    
    print("✅ 用户交互日志测试完成")

def test_symptom_extractor_logging():
    """测试SymptomExtractor的日志功能"""
    print("🧪 测试SymptomExtractor日志功能...")
    
    try:
        # 初始化SymptomExtractor（这会触发RAG系统初始化日志）
        extractor = SymptomExtractor()
        print("✅ SymptomExtractor初始化日志测试完成")
        
        # 测试诊断建议生成（模拟症状）
        test_symptoms = "患者出现头痛、发热、咳嗽等症状"
        print(f"🔍 测试症状: {test_symptoms}")
        
        # 这会触发RAG检索和日志记录
        result = extractor.generate_diagnosis_advice(test_symptoms)
        print(f"📋 诊断建议: {result[:100]}...")
        
        print("✅ 诊断建议生成日志测试完成")
        
    except Exception as e:
        print(f"⚠️ SymptomExtractor测试出现异常: {e}")
        log_error(f"SymptomExtractor测试异常: {e}", exc_info=True)

def check_log_files():
    """检查日志文件是否正确生成"""
    print("🧪 检查日志文件...")
    
    log_dir = "logs"
    expected_files = [
        "medical_chat.log",
        "error.log", 
        "rag_system.log",
        "api_calls.log"
    ]
    
    if not os.path.exists(log_dir):
        print(f"❌ 日志目录 {log_dir} 不存在")
        return False
    
    for log_file in expected_files:
        file_path = os.path.join(log_dir, log_file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {log_file}: {file_size} bytes")
        else:
            print(f"❌ {log_file}: 文件不存在")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始日志功能测试...")
    print("=" * 50)
    
    # 基本日志测试
    test_basic_logging()
    print()
    
    # API日志测试
    test_api_logging()
    print()
    
    # RAG日志测试
    test_rag_logging()
    print()
    
    # 用户交互日志测试
    test_user_interaction_logging()
    print()
    
    # SymptomExtractor日志测试
    test_symptom_extractor_logging()
    print()
    
    # 等待一下让日志写入完成
    time.sleep(1)
    
    # 检查日志文件
    check_log_files()
    print()
    
    print("=" * 50)
    print("🎉 日志功能测试完成！")
    print("📁 请检查 logs/ 目录下的日志文件")

if __name__ == "__main__":
    main()
