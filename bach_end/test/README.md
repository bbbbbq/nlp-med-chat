# 测试目录说明

本目录包含医疗AI聊天应用后端的所有测试文件。

## 测试文件列表

### RAG系统测试
- **`test_rag.py`** - 基础医学RAG系统功能测试
- **`test_large_rag.py`** - 大规模医学RAG系统测试
- **`test_large_scale_rag.py`** - 2000条知识库的大规模RAG系统完整测试

### 工作流程测试
- **`test_full_workflow.py`** - 完整的RAG增强医疗诊断工作流程测试

### 基础功能测试
- **`chat_test.py`** - 聊天功能基础测试
- **`smns_test.py`** - 症状提取功能测试

## 运行测试

从backend根目录运行测试：

```bash
# 运行大规模RAG系统测试
python3 test/test_large_scale_rag.py

# 运行完整工作流程测试
python3 test/test_full_workflow.py

# 运行基础RAG测试
python3 test/test_rag.py

# 运行其他测试
python3 test/test_large_rag.py
python3 test/chat_test.py
python3 test/smns_test.py
```

## 测试覆盖范围

- ✅ 医学知识库加载和初始化
- ✅ 症状检索和匹配
- ✅ RAG增强诊断建议生成
- ✅ 多症状复合查询
- ✅ 系统性能和响应时间
- ✅ 多医学专科分类覆盖
- ✅ DeepSeek API集成
