#!/usr/bin/env python3
"""
测试大规模医学RAG系统
"""

import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import MedicalRAGRetriever, MedicalKnowledgeBase
from rag.data.medical_knowledge_data import get_medical_knowledge_count, get_all_categories

def test_large_rag_system():
    """测试大规模RAG系统"""
    print("🧪 开始测试大规模医学RAG系统")
    print("=" * 60)
    
    # 1. 测试知识库规模
    print(f"📊 医学知识库统计:")
    print(f"   - 总条目数: {get_medical_knowledge_count()}")
    print(f"   - 疾病分类: {len(get_all_categories())} 个")
    print(f"   - 分类列表: {', '.join(get_all_categories())}")
    print()
    
    # 2. 初始化RAG系统
    print("🔧 初始化RAG检索系统...")
    try:
        # MedicalKnowledgeBase已通过rag包导入
        # 先创建知识库实例
        knowledge_base = MedicalKnowledgeBase()
        # 再创建RAG检索器
        rag_retriever = MedicalRAGRetriever(knowledge_base)
        print("✅ RAG系统初始化成功")
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        return
    print()
    
    # 3. 测试不同类型的症状检索
    test_cases = [
        {
            "name": "呼吸系统症状",
            "symptoms": "患者出现咳嗽、发热、胸痛、呼吸困难等症状",
            "expected_categories": ["呼吸系统疾病"]
        },
        {
            "name": "心血管症状", 
            "symptoms": "患者有胸闷、心悸、头晕、血压升高的表现",
            "expected_categories": ["心血管疾病"]
        },
        {
            "name": "消化系统症状",
            "symptoms": "患者主诉上腹痛、恶心呕吐、食欲不振",
            "expected_categories": ["消化系统疾病"]
        },
        {
            "name": "神经系统症状",
            "symptoms": "患者突然出现偏瘫、失语、面瘫等症状",
            "expected_categories": ["神经系统疾病"]
        },
        {
            "name": "内分泌症状",
            "symptoms": "患者有多饮、多尿、多食、体重下降的症状",
            "expected_categories": ["内分泌疾病"]
        },
        {
            "name": "骨科症状",
            "symptoms": "患者外伤后出现疼痛、肿胀、功能障碍",
            "expected_categories": ["骨科疾病"]
        },
        {
            "name": "复合症状",
            "symptoms": "患者有发热、咳嗽、胸痛，同时伴有心悸、胸闷",
            "expected_categories": ["呼吸系统疾病", "心血管疾病"]
        }
    ]
    
    print("🔍 开始症状检索测试:")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"症状描述: {test_case['symptoms']}")
        
        try:
            # 执行RAG检索
            results = rag_retriever.knowledge_base.search_relevant_knowledge(test_case['symptoms'], top_k=3)
            
            if results:
                print(f"✅ 检索到 {len(results)} 条相关知识:")
                
                found_categories = set()
                for j, result in enumerate(results, 1):
                    disease = result.get('disease', '未知')
                    category = result.get('category', '未知')
                    score = result.get('score', 0)
                    found_categories.add(category)
                    
                    print(f"   {j}. {disease} ({category}) - 相关度: {score:.3f}")
                
                # 检查是否找到了预期的疾病分类
                expected_set = set(test_case['expected_categories'])
                if expected_set.intersection(found_categories):
                    print(f"✅ 成功匹配预期分类: {expected_set.intersection(found_categories)}")
                else:
                    print(f"⚠️ 未完全匹配预期分类，预期: {expected_set}, 实际: {found_categories}")
                    
            else:
                print("❌ 未检索到相关知识")
                
        except Exception as e:
            print(f"❌ 检索失败: {e}")
    
    print("\n" + "=" * 60)
    
    # 4. 测试RAG增强的诊断建议生成
    print("🩺 测试RAG增强诊断建议生成:")
    print("-" * 60)
    
    test_symptoms = "患者男性，45岁，主诉胸痛、呼吸困难、咳嗽伴发热3天"
    print(f"测试症状: {test_symptoms}")
    
    try:
        # 获取RAG增强的提示词
        enhanced_prompt = rag_retriever.retrieve_and_format(test_symptoms)
        
        print("\n📋 RAG增强提示词预览:")
        print("-" * 40)
        # 只显示前500个字符
        preview = enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt
        print(preview)
        
        print(f"\n📊 提示词统计:")
        print(f"   - 总长度: {len(enhanced_prompt)} 字符")
        print(f"   - 包含医学知识: {'是' if '医学知识参考' in enhanced_prompt else '否'}")
        print(f"   - 包含症状分析: {'是' if test_symptoms in enhanced_prompt else '否'}")
        
    except Exception as e:
        print(f"❌ RAG增强失败: {e}")
    
    print("\n🎉 大规模医学RAG系统测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_large_rag_system()
