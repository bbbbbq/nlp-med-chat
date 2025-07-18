"""
医学RAG系统 - 为诊断建议提供知识库支持
"""

import os
import json
import numpy as np
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import jieba
import re

# 导入日志功能
try:
    from logger_config import log_info, log_error, log_rag_operation
except ImportError:
    # 如果日志模块不可用，使用空函数
    def log_info(msg): pass
    def log_error(msg, exc_info=False): pass
    def log_rag_operation(operation, query, score=None, count=None): pass

# 医学知识库数据导入
try:
    from .data.large_medical_knowledge_data import LARGE_MEDICAL_KNOWLEDGE_DATABASE
except ImportError:
    try:
        from .data.medical_knowledge_data import MEDICAL_KNOWLEDGE_DATABASE
    except ImportError:
        LARGE_MEDICAL_KNOWLEDGE_DATABASE = None
        MEDICAL_KNOWLEDGE_DATABASE = None


class MedicalKnowledgeBase:
    """医学知识库管理器"""
    
    def __init__(self, db_path: str = "./rag/data/medical_knowledge_db"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = "medical_knowledge"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 初始化或获取集合
        log_info(f"开始初始化医学知识库，数据库路径: {db_path}")
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            count = self.collection.count()
            print(f"✅ 已加载现有医学知识库，包含 {count} 条记录")
            log_info(f"加载现有医学知识库，包含 {count} 条记录")
            # 加载现有数据库时也需要初始化知识库数据
            self._load_knowledge_database()
        except Exception as e:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"描述": "医学诊断知识库"}
            )
            print("🆕 创建新的医学知识库")
            log_info("创建新的医学知识库")
            self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化医学知识库"""
        # 使用顶部导入的医学知识库数据
        if LARGE_MEDICAL_KNOWLEDGE_DATABASE is not None:
            self.medical_knowledge_database = LARGE_MEDICAL_KNOWLEDGE_DATABASE
            print(f"✅ 成功加载大规模医学知识库，包含 {len(self.medical_knowledge_database)} 条记录")
        elif MEDICAL_KNOWLEDGE_DATABASE is not None:
            self.medical_knowledge_database = MEDICAL_KNOWLEDGE_DATABASE
            print(f"✅ 成功加载原医学知识库，包含 {len(self.medical_knowledge_database)} 条记录")
        else:
            print("⚠️  无法导入医学知识库，使用默认数据")
            self.medical_knowledge_database = [
                    {
                        "id": "pneumonia_001",
                        "category": "呼吸系统疾病",
                        "disease": "肺炎",
                        "symptoms": ["咳嗽", "发热", "胸痛", "呼吸困难"],
                        "imaging_findings": ["肺部阴影", "实变", "磨玻璃影"],
                        "diagnosis_criteria": "临床症状 + 胸部影像学检查 + 血常规",
                        "treatment": "抗生素治疗、支持治疗",
                        "severity": ["轻度", "中度", "重度"],
                        "content": "肺炎是肺实质的急性感染性炎症，主要表现为发热、咳嗽、胸痛等症状。"
                    }
                ]
        
        # 添加知识到向量数据库
        documents = []
        metadatas = []
        ids = []
        
        for knowledge in self.medical_knowledge_database:
            # 构建文档内容
            doc_content = f"""
疾病：{knowledge['disease']}
分类：{knowledge['category']}
描述：{knowledge['description']}
症状：{', '.join(knowledge['symptoms']) if knowledge['symptoms'] else '无明显症状'}
病因：{knowledge['causes']}
预防：{knowledge['prevention']}
治疗：{', '.join(knowledge['treatment']) if isinstance(knowledge['treatment'], list) else knowledge['treatment']}
诊断方法：{', '.join(knowledge['diagnosis_methods']) if knowledge['diagnosis_methods'] else '临床诊断'}
严重程度：{knowledge['severity']}
影像表现：{', '.join(knowledge['imaging_findings']) if knowledge['imaging_findings'] else '需要进一步检查'}
"""
            
            # 转换metadata中的列表为字符串（ChromaDB不支持列表类型）
            metadata = {
                'id': f"{knowledge['category']}_{knowledge['disease']}",
                'category': knowledge['category'],
                'disease': knowledge['disease'],
                'symptoms': ', '.join(knowledge['symptoms']) if knowledge['symptoms'] else '',
                'causes': knowledge['causes'],
                'prevention': knowledge['prevention'],
                'treatment': ', '.join(knowledge['treatment']) if isinstance(knowledge['treatment'], list) else knowledge['treatment'],
                'diagnosis_methods': ', '.join(knowledge['diagnosis_methods']) if knowledge['diagnosis_methods'] else '',
                'severity': knowledge['severity'],
                'imaging_findings': ', '.join(knowledge['imaging_findings']) if knowledge['imaging_findings'] else '',
                'description': knowledge['description']
            }
            
            documents.append(doc_content)
            metadatas.append(metadata)
            ids.append(f"{knowledge['category']}_{knowledge['disease']}_{len(documents)}")
        
        # 批量添加到向量数据库
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ 已初始化 {len(self.medical_knowledge_database)} 条医学知识记录")
    
    def _load_knowledge_database(self):
        """加载知识库数据（用于已存在的数据库）"""
        if LARGE_MEDICAL_KNOWLEDGE_DATABASE is not None:
            self.medical_knowledge_database = LARGE_MEDICAL_KNOWLEDGE_DATABASE
        elif MEDICAL_KNOWLEDGE_DATABASE is not None:
            self.medical_knowledge_database = MEDICAL_KNOWLEDGE_DATABASE
        else:
            # 如果都无法导入，设置为空列表
            self.medical_knowledge_database = []
    
    def get_knowledge_count(self) -> int:
        """获取知识库中的条目数量"""
        return len(self.medical_knowledge_database)
    
    def search_relevant_knowledge(self, symptoms: str, top_k: int = 3) -> List[Dict]:
        """根据症状搜索相关医学知识"""
        print(f"🔍 正在搜索与症状相关的医学知识: {symptoms[:100]}...")
        log_rag_operation("知识搜索", symptoms[:100], knowledge_count=top_k)
    
        # 使用向量搜索
        results = self.collection.query(
            query_texts=[symptoms],
            n_results=top_k
        )
        
        relevant_knowledge = []
        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            for i, metadata in enumerate(results['metadatas'][0]):
                distance = results['distances'][0][i] if results['distances'] else 0
                knowledge = {
                    'disease': metadata['disease'],
                    'category': metadata['category'],
                    'symptoms': metadata['symptoms'].split(', ') if isinstance(metadata['symptoms'], str) and metadata['symptoms'] else [],
                    'causes': metadata.get('causes', ''),
                    'prevention': metadata.get('prevention', ''),
                    'treatment': metadata['treatment'],
                    'diagnosis_methods': metadata.get('diagnosis_methods', '').split(', ') if metadata.get('diagnosis_methods') else [],
                    'severity': metadata.get('severity', ''),
                    'imaging_findings': metadata.get('imaging_findings', '').split(', ') if metadata.get('imaging_findings') else [],
                    'description': metadata.get('description', ''),
                    'metadata': metadata,  # 保留原始 metadata
                    'distance': distance,
                    'relevance_score': 1 - distance  # 转换为相似度分数
                }
                relevant_knowledge.append(knowledge)
        
        print(f"📚 找到 {len(relevant_knowledge)} 条相关医学知识")
        
        # 记录搜索结果
        if relevant_knowledge:
            max_score = max([k['relevance_score'] for k in relevant_knowledge])
            log_rag_operation("搜索结果", f"找到{len(relevant_knowledge)}条知识", max_score, len(relevant_knowledge))
        else:
            log_rag_operation("搜索结果", "未找到相关知识", 0, 0)
        
        return relevant_knowledge

    def add_knowledge(self, knowledge_data: Dict):
        """添加新的医学知识"""
        doc_content = f"""
疾病：{knowledge_data['disease']}
分类：{knowledge_data['category']}
症状：{', '.join(knowledge_data['symptoms'])}
影像表现：{', '.join(knowledge_data['imaging_findings'])}
诊断标准：{knowledge_data['diagnosis_criteria']}
治疗方案：{knowledge_data['treatment']}
详细描述：{knowledge_data['content']}
"""
        
        # 转换metadata中的列表为字符串
        metadata = {
            'id': knowledge_data['id'],
            'category': knowledge_data['category'],
            'disease': knowledge_data['disease'],
            'symptoms': ', '.join(knowledge_data['symptoms']) if isinstance(knowledge_data['symptoms'], list) else knowledge_data['symptoms'],
            'imaging_findings': ', '.join(knowledge_data['imaging_findings']) if isinstance(knowledge_data['imaging_findings'], list) else knowledge_data['imaging_findings'],
            'diagnosis_criteria': knowledge_data['diagnosis_criteria'],
            'treatment': knowledge_data['treatment'],
            'severity': ', '.join(knowledge_data.get('severity', [])) if isinstance(knowledge_data.get('severity'), list) else knowledge_data.get('severity', ''),
            'content': knowledge_data['content']
        }
        
        self.collection.add(
            documents=[doc_content],
            metadatas=[metadata],
            ids=[knowledge_data['id']]
        )
        print(f"✅ 已添加新的医学知识: {knowledge_data['disease']}")


class MedicalRAGRetriever:
    """医学RAG检索器"""
    
    def __init__(self, knowledge_base: MedicalKnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def retrieve_and_format(self, symptoms: str, top_k: int = 3) -> str:
        """检索并格式化医学知识"""
        relevant_knowledge = self.knowledge_base.search_relevant_knowledge(symptoms, top_k)
        
        if not relevant_knowledge:
            return "未找到相关医学知识。"
        
        formatted_knowledge = "**相关医学知识参考：**\n\n"
        
        for i, knowledge in enumerate(relevant_knowledge, 1):
            formatted_knowledge += f"### {i}. {knowledge['disease']} ({knowledge['category']})\n"
            if knowledge.get('symptoms'):
                formatted_knowledge += f"**常见症状：** {', '.join(knowledge['symptoms'])}\n"
            if knowledge.get('imaging_findings'):
                formatted_knowledge += f"**影像表现：** {', '.join(knowledge['imaging_findings'])}\n"
            if knowledge.get('diagnosis_criteria'):
                formatted_knowledge += f"**诊断标准：** {knowledge['diagnosis_criteria']}\n"
            if knowledge.get('diagnosis_methods'):
                formatted_knowledge += f"**诊断方法：** {', '.join(knowledge['diagnosis_methods'])}\n"
            if knowledge.get('treatment'):
                formatted_knowledge += f"**治疗方案：** {knowledge['treatment']}\n"
            if knowledge.get('causes'):
                formatted_knowledge += f"**病因：** {knowledge['causes'][:200]}\n"  # 限制长度
            if knowledge.get('content'):
                formatted_knowledge += f"**详细说明：** {knowledge['content']}\n"
            formatted_knowledge += f"**相关度：** {knowledge['relevance_score']:.2f}\n\n"
            formatted_knowledge += "---\n\n"
        
        return formatted_knowledge
    
    def format_knowledge_for_diagnosis(self, relevant_knowledge: List[Dict]) -> str:
        """为诊断建议生成格式化医学知识"""
        if not relevant_knowledge:
            return "未找到相关医学知识。"
        
        formatted_knowledge = "相关医学知识参考：\n\n"
        
        for i, knowledge in enumerate(relevant_knowledge, 1):
            formatted_knowledge += f"{i}. 疾病：{knowledge['disease']} (分类：{knowledge['category']})\n"
            if knowledge.get('symptoms'):
                formatted_knowledge += f"   常见症状：{', '.join(knowledge['symptoms'][:5])}\n"  # 只显示前5个症状
            if knowledge.get('causes'):
                formatted_knowledge += f"   病因：{knowledge['causes'][:100]}\n"  # 限制长度
            if knowledge.get('treatment'):
                formatted_knowledge += f"   治疗：{knowledge['treatment'][:100]}\n"
            if knowledge.get('diagnosis_methods'):
                formatted_knowledge += f"   诊断方法：{', '.join(knowledge['diagnosis_methods'][:3])}\n"
            formatted_knowledge += f"   相关度：{knowledge['relevance_score']:.3f}\n\n"
        
        return formatted_knowledge


def initialize_medical_rag():
    """初始化医学RAG系统"""
    print("🚀 正在初始化医学RAG系统...")
    
    # 创建知识库
    knowledge_base = MedicalKnowledgeBase()
    
    # 创建检索器
    retriever = MedicalRAGRetriever(knowledge_base)
    
    print("✅ 医学RAG系统初始化完成")
    return knowledge_base, retriever


if __name__ == "__main__":
    # 测试RAG系统
    kb, retriever = initialize_medical_rag()
    
    # 测试检索
    test_symptoms = "患者出现咳嗽、发热、胸痛症状，影像显示肺部阴影"
    result = retriever.retrieve_and_format(test_symptoms)
    print("检索结果：")
    print(result)
