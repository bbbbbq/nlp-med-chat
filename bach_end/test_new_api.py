#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的诊断API集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import SymptomExtractor

def test_diagnosis_api():
    """测试诊断API功能"""
    print("🧪 开始测试新的诊断API集成...")
    
    # 初始化症状提取器
    extractor = SymptomExtractor()
    
    # 测试症状
    test_symptoms = """
    【影像类型】：胸部X光片
    【观察到的症状】：
    1. 右肺下叶可见片状阴影
    2. 肺纹理增粗
    3. 心影轮廓清晰
    【异常区域】：右肺下叶
    【严重程度】：中等
    """
    
    print("📝 测试症状信息:")
    print(test_symptoms)
    print("\n" + "="*50)
    
    # 调用诊断建议生成
    print("🩺 开始生成诊断建议...")
    diagnosis_result = extractor.generate_diagnosis_advice(test_symptoms)
    
    print("\n" + "="*50)
    print("📋 诊断结果:")
    print(diagnosis_result)
    
    return diagnosis_result

def test_direct_diagnosis_api():
    """直接测试诊断API调用"""
    print("\n🔧 直接测试诊断API调用...")
    
    extractor = SymptomExtractor()
    
    test_prompt = """
    请根据以下症状提供医学诊断建议：
    
    患者症状：
    - 持续咳嗽2周
    - 胸部疼痛
    - 轻微发热
    
    请提供可能的诊断和建议。
    """
    
    result = extractor.chat_with_diagnosis_api(test_prompt)
    
    print("📋 直接API调用结果:")
    print(result)
    
    return result

if __name__ == "__main__":
    print("🚀 开始测试新的诊断API集成...")
    
    try:
        # 测试1：完整的诊断建议生成流程
        print("\n" + "="*60)
        print("测试1：完整的诊断建议生成流程")
        print("="*60)
        test_diagnosis_api()
        
        # 测试2：直接API调用
        print("\n" + "="*60)
        print("测试2：直接诊断API调用")
        print("="*60)
        test_direct_diagnosis_api()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
