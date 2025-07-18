# RAG (Retrieval-Augmented Generation) 模块

本目录包含医疗AI聊天应用的RAG系统相关文件。

## 目录结构

```
rag/
├── __init__.py                          # RAG模块初始化
├── medical_rag.py                       # 核心RAG系统实现
├── process_large_medical_data.py        # 大规模医学数据处理脚本
├── data/                               # RAG数据目录
│   ├── __init__.py                     # 数据模块初始化
│   ├── medical_knowledge_data.py       # 原始医学知识库数据
│   ├── large_medical_knowledge_data.py # 大规模医学知识库数据(2000条)
│   ├── medical.json                    # 原始医学数据JSON文件
│   ├── medical_kg_entity.json          # 医学知识图谱实体数据
│   └── medical_knowledge_db/           # ChromaDB向量数据库存储
└── README.md                           # 本说明文件
```

## 核心功能

### 1. 医学知识库管理 (`MedicalKnowledgeBase`)
- 加载和管理医学知识数据
- 支持大规模知识库(2000+条记录)
- ChromaDB向量存储和检索
- 自动初始化和数据预处理

### 2. RAG检索器 (`MedicalRAGRetriever`)
- 基于症状的语义检索
- 多症状复合查询支持
- 相关度评分和排序
- 知识格式化输出

### 3. 数据处理工具
- 原始医学数据清洗和转换
- 症状提取和分类
- 知识库格式标准化
- 批量数据处理

## 技术特性

- **大规模知识库**: 支持2000+条医学知识记录
- **多专科覆盖**: 15+个医学专科分类
- **高效检索**: <1秒响应时间
- **语义匹配**: 基于sentence-transformers的向量检索
- **兼容性**: 支持ChromaDB metadata限制的数据格式

## 使用方法

```python
from rag import initialize_medical_rag, MedicalRAGRetriever

# 初始化RAG系统
knowledge_base, rag_retriever = initialize_medical_rag()

# 检索相关医学知识
symptoms = "咳嗽、胸痛、发热"
results = rag_retriever.search_relevant_knowledge(symptoms, top_k=5)

# 格式化诊断建议
formatted_knowledge = rag_retriever.format_knowledge_for_diagnosis(results)
```

## 数据来源

- **原始数据**: 8808条医学知识记录
- **处理后数据**: 2000条高质量医学知识
- **覆盖范围**: 呼吸、心血管、神经、消化、眼科、妇科等多个专科
- **数据字段**: 疾病名称、症状、病因、预防、治疗、诊断方法等

## 性能指标

- ✅ 知识库规模: 2000条记录
- ✅ 检索响应时间: <1秒
- ✅ 专科覆盖: 15+个分类
- ✅ 症状匹配准确率: 高精度语义匹配
- ✅ 系统稳定性: 经过全面测试验证
