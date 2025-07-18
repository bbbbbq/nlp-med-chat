#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的诊断API参数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import SymptomExtractor

def test_optimized_diagnosis():
    """测试优化后的诊断API调用"""
    print("🧪 测试优化后的诊断API参数...")
    
    # 创建症状提取器实例
    extractor = SymptomExtractor()
    
    # 模拟症状信息
    test_symptoms = """
【影像类型】：胸部X光片
【观察到的症状】：
1. 双肺纹理增粗
2. 右下肺野可见片状阴影
3. 肺门结构清晰
【异常区域】：右下肺野
【严重程度】：中等
"""
    
    print("📝 测试症状信息:")
    print(test_symptoms)
    print("\n" + "="*50)
    
    # 调用优化后的诊断API
    print("🚀 调用优化后的诊断API...")
    result = extractor.chat_with_diagnosis_api(
        extractor.diagnosis_prompt.format(symptoms=test_symptoms)
    )
    
    print("\n📋 诊断结果:")
    print("="*50)
    print(result)
    print("="*50)
    
    # 检查结果质量
    if result and len(result) > 0:
        print("✅ API调用成功")
        
        # 检查是否包含重复内容
        if "《中华结核和呼吸杂志》" in result:
            print("⚠️  检测到重复的参考资料内容")
        else:
            print("✅ 未检测到重复内容")
            
        # 检查长度是否合理
        if len(result) > 2000:
            print(f"⚠️  输出较长: {len(result)} 字符")
        else:
            print(f"✅ 输出长度合理: {len(result)} 字符")
            
    else:
        print("❌ API调用失败")

if __name__ == "__main__":
    test_optimized_diagnosis()
