#!/usr/bin/env python3
"""
测试高匹配度症状，尝试触发RAG增强诊断
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import SymptomExtractor

def test_high_match_symptoms():
    """测试高匹配度症状"""
    print("🧪 测试高匹配度症状...")
    
    # 初始化症状提取器
    extractor = SymptomExtractor()
    
    # 使用更具体的医学术语，可能会有更高的匹配度
    specific_symptoms = [
        # 心血管系统
        """
        【影像类型】：心电图和胸部X光
        【观察到的症状】：
        1. 心律不齐
        2. ST段抬高
        3. 心肌缺血
        4. 冠状动脉狭窄
        【异常区域】：心脏冠状动脉
        【严重程度】：严重
        """,
        
        # 呼吸系统
        """
        【影像类型】：胸部CT
        【观察到的症状】：
        1. 肺部结节
        2. 支气管扩张
        3. 肺气肿
        4. 胸腔积液
        【异常区域】：双侧肺野
        【严重程度】：中等
        """,
        
        # 消化系统
        """
        【影像类型】：腹部CT
        【观察到的症状】：
        1. 肝脏肿大
        2. 胆囊炎
        3. 胰腺炎
        4. 腹腔积液
        【异常区域】：腹腔器官
        【严重程度】：中等
        """,
        
        # 神经系统
        """
        【影像类型】：头部MRI
        【观察到的症状】：
        1. 脑梗塞
        2. 脑出血
        3. 颅内压增高
        4. 脑水肿
        【异常区域】：大脑皮层
        【严重程度】：严重
        """
    ]
    
    for i, symptoms in enumerate(specific_symptoms, 1):
        print(f"\n{'='*60}")
        print(f"📋 测试用例{i}：具体医学症状")
        print("="*60)
        print("输入症状：", symptoms.strip())
        
        result = extractor.generate_diagnosis_advice(symptoms)
        print(f"\n诊断结果：{result[:300]}..." if len(result) > 300 else result)

if __name__ == "__main__":
    test_high_match_symptoms()
