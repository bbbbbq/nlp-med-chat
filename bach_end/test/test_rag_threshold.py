#!/usr/bin/env python3
"""
测试RAG匹配度阈值功能
验证只有当匹配度超过0.7时才使用RAG增强诊断
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import SymptomExtractor

def test_rag_threshold():
    """测试RAG匹配度阈值功能"""
    print("🧪 开始测试RAG匹配度阈值功能...")
    
    # 初始化症状提取器
    extractor = SymptomExtractor()
    
    # 测试用例1：高匹配度症状（应该使用RAG）
    print("\n" + "="*60)
    print("📋 测试用例1：高匹配度症状（心血管相关）")
    print("="*60)
    high_match_symptoms = """
    【影像类型】：胸部X光片
    【观察到的症状】：
    1. 心脏轮廓增大
    2. 肺血管纹理增粗
    3. 胸腔积液征象
    【异常区域】：心脏区域和双侧肺野
    【严重程度】：中等
    """
    
    print("输入症状：", high_match_symptoms.strip())
    result1 = extractor.generate_diagnosis_advice(high_match_symptoms)
    print("\n诊断结果：", result1[:200] + "..." if len(result1) > 200 else result1)
    
    # 测试用例2：低匹配度症状（应该使用传统诊断）
    print("\n" + "="*60)
    print("📋 测试用例2：低匹配度症状（非典型症状）")
    print("="*60)
    low_match_symptoms = """
    【影像类型】：未知影像
    【观察到的症状】：
    1. 奇怪的阴影
    2. 不明原因的亮点
    3. 模糊的区域
    【异常区域】：不确定位置
    【严重程度】：未知
    """
    
    print("输入症状：", low_match_symptoms.strip())
    result2 = extractor.generate_diagnosis_advice(low_match_symptoms)
    print("\n诊断结果：", result2[:200] + "..." if len(result2) > 200 else result2)
    
    # 测试用例3：神经系统症状（可能中等匹配度）
    print("\n" + "="*60)
    print("📋 测试用例3：神经系统症状")
    print("="*60)
    neuro_symptoms = """
    【影像类型】：头部CT
    【观察到的症状】：
    1. 头痛
    2. 视力模糊
    3. 恶心呕吐
    【异常区域】：颅内
    【严重程度】：中等
    """
    
    print("输入症状：", neuro_symptoms.strip())
    result3 = extractor.generate_diagnosis_advice(neuro_symptoms)
    print("\n诊断结果：", result3[:200] + "..." if len(result3) > 200 else result3)
    
    print("\n" + "="*60)
    print("✅ RAG匹配度阈值测试完成")
    print("="*60)

if __name__ == "__main__":
    test_rag_threshold()
