#!/usr/bin/env python3
"""
测试医学RAG系统
"""

import sys
import os
import traceback

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import initialize_medical_rag
from chat import SymptomExtractor

def test_rag_system():
    """测试RAG系统基本功能"""
    print("🧪 开始测试医学RAG系统...")
    
    try:
        # 1. 测试RAG系统初始化
        print("\n1️⃣ 测试RAG系统初始化...")
        knowledge_base, retriever = initialize_medical_rag()
        print("✅ RAG系统初始化成功")
        
        # 2. 测试知识检索
        print("\n2️⃣ 测试知识检索功能...")
        test_symptoms = [
            "患者出现咳嗽、发热、胸痛症状，影像显示肺部阴影",
            "患者右下腹疼痛，伴有发热和恶心",
            "患者出现头痛、头晕、血压升高",
            "患者多饮多尿，血糖升高"
        ]
        
        for i, symptom in enumerate(test_symptoms, 1):
            print(f"\n测试症状 {i}: {symptom}")
            result = retriever.retrieve_and_format(symptom, top_k=2)
            print("检索结果:")
            print(result[:300] + "..." if len(result) > 300 else result)
            print("-" * 50)
        
        # 3. 测试完整的症状提取器
        print("\n3️⃣ 测试完整的症状提取器...")
        extractor = SymptomExtractor()
        
        if extractor.rag_retriever:
            print("✅ 症状提取器中的RAG系统初始化成功")
            
            # 测试诊断建议生成
            test_symptom = """
【影像类型】：胸部X光片
【观察到的症状】：
1. 右肺下叶可见片状阴影
2. 肺纹理增粗
3. 胸腔少量积液
【异常区域】：右肺下叶
【严重程度】：中等
"""
            print(f"\n测试症状: {test_symptom}")
            print("\n正在生成RAG增强的诊断建议...")
            # 注意：这里不会真正调用DeepSeek API，只是测试RAG检索部分
            
        else:
            print("❌ 症状提取器中的RAG系统初始化失败")
        
        print("\n🎉 RAG系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        # traceback已在文件顶部导入
        traceback.print_exc()

def test_knowledge_search():
    """测试知识搜索功能"""
    print("\n🔍 测试知识搜索功能...")
    
    try:
        kb, retriever = initialize_medical_rag()
        
        # 测试不同类型的搜索
        search_queries = [
            "肺炎",
            "骨折",
            "发热咳嗽",
            "右下腹痛",
            "高血压头痛",
            "多饮多尿"
        ]
        
        for query in search_queries:
            print(f"\n搜索: {query}")
            knowledge = kb.search_relevant_knowledge(query, top_k=2)
            for k in knowledge:
                print(f"- {k['disease']} ({k['category']}) - 相关度: {k['relevance_score']:.3f}")
        
    except Exception as e:
        print(f"❌ 知识搜索测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 医学RAG系统测试")
    print("=" * 60)
    
    test_rag_system()
    test_knowledge_search()
    
    print("\n" + "=" * 60)
    print("测试完成！")
