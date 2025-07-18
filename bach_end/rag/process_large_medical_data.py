#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大规模医疗知识数据处理脚本
将下载的医疗知识图谱数据转换为RAG系统可用的格式
"""

import json
import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """清理文本，去除多余的空白字符和特殊符号"""
    if not isinstance(text, str):
        return str(text)
    
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    # 去除一些特殊符号
    text = re.sub(r'[^\w\s\u4e00-\u9fff，。；：！？、（）【】《》""''％%]', '', text)
    return text

def extract_symptoms_from_text(desc: str, symptom_list: List[str]) -> List[str]:
    """从描述文本中提取症状关键词"""
    symptoms = set()
    
    # 添加明确的症状列表
    if symptom_list:
        symptoms.update(symptom_list)
    
    # 从描述中提取常见症状关键词
    symptom_keywords = [
        '疼痛', '发热', '咳嗽', '呼吸困难', '胸痛', '头痛', '恶心', '呕吐', 
        '腹痛', '腹泻', '便秘', '乏力', '头晕', '失眠', '食欲不振', '体重下降',
        '皮疹', '瘙痒', '水肿', '出血', '紫绀', '黄疸', '贫血', '心悸',
        '气短', '胸闷', '咯血', '盗汗', '寒战', '关节痛', '肌肉痛', '麻木'
    ]
    
    for keyword in symptom_keywords:
        if keyword in desc:
            symptoms.add(keyword)
    
    return list(symptoms)

def categorize_disease(category_list: List[str], name: str) -> str:
    """根据分类信息确定疾病类别"""
    if not category_list:
        return "其他疾病"
    
    # 定义分类映射
    category_mapping = {
        '呼吸内科': '呼吸系统疾病',
        '心血管内科': '心血管疾病', 
        '消化内科': '消化系统疾病',
        '神经内科': '神经系统疾病',
        '内分泌科': '内分泌疾病',
        '泌尿外科': '泌尿系统疾病',
        '骨科': '骨科疾病',
        '外科': '外科疾病',
        '妇产科': '妇科疾病',
        '皮肤科': '皮肤疾病',
        '眼科': '眼科疾病',
        '耳鼻喉科': '耳鼻喉疾病',
        '精神科': '精神疾病',
        '儿科': '儿科疾病'
    }
    
    # 检查分类列表中的科室
    for cat in category_list:
        for dept, disease_type in category_mapping.items():
            if dept in cat:
                return disease_type
    
    # 根据疾病名称推断分类
    if any(keyword in name for keyword in ['肺', '呼吸', '咳嗽', '气管', '支气管']):
        return '呼吸系统疾病'
    elif any(keyword in name for keyword in ['心', '血管', '动脉', '静脉']):
        return '心血管疾病'
    elif any(keyword in name for keyword in ['胃', '肠', '肝', '胆', '胰', '消化']):
        return '消化系统疾病'
    elif any(keyword in name for keyword in ['脑', '神经', '头痛', '癫痫']):
        return '神经系统疾病'
    elif any(keyword in name for keyword in ['糖尿病', '甲状腺', '内分泌']):
        return '内分泌疾病'
    elif any(keyword in name for keyword in ['肾', '膀胱', '尿', '泌尿']):
        return '泌尿系统疾病'
    elif any(keyword in name for keyword in ['骨', '关节', '肌肉', '韧带']):
        return '骨科疾病'
    elif any(keyword in name for keyword in ['皮肤', '湿疹', '皮炎']):
        return '皮肤疾病'
    else:
        return '其他疾病'

def process_medical_data(input_file: str, output_file: str, max_records: int = None):
    """处理医疗数据并转换为RAG系统格式"""
    processed_data = []
    
    print(f"🔄 开始处理医疗知识数据...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            if max_records and len(processed_data) >= max_records:
                break
                
            if line.strip():
                try:
                    data = json.loads(line.strip())
                    
                    # 提取基本信息
                    name = data.get('name', '').strip()
                    desc = data.get('desc', '').strip()
                    category_list = data.get('category', [])
                    symptom_list = data.get('symptom', [])
                    cause = data.get('cause', '').strip()
                    prevent = data.get('prevent', '').strip()
                    cure_way = data.get('cure_way', [])
                    check_methods = data.get('check', [])
                    
                    if not name or not desc:
                        continue
                    
                    # 清理和处理数据
                    name = clean_text(name)
                    desc = clean_text(desc)
                    cause = clean_text(cause)
                    prevent = clean_text(prevent)
                    
                    # 提取症状
                    symptoms = extract_symptoms_from_text(desc + ' ' + cause, symptom_list)
                    
                    # 确定疾病分类
                    disease_category = categorize_disease(category_list, name)
                    
                    # 构建RAG格式的数据
                    rag_entry = {
                        'disease': name,
                        'category': disease_category,
                        'description': desc,
                        'symptoms': symptoms[:10],  # 限制症状数量
                        'causes': cause if cause else '病因不明',
                        'prevention': prevent if prevent else '暂无预防措施',
                        'treatment': cure_way[:5] if cure_way else ['对症治疗'],
                        'diagnosis_methods': check_methods[:5] if check_methods else ['临床诊断'],
                        'severity': '中等',  # 默认严重程度
                        'imaging_findings': ['需要进一步检查']  # 默认影像学表现
                    }
                    
                    processed_data.append(rag_entry)
                    
                    if len(processed_data) % 1000 == 0:
                        print(f"✅ 已处理 {len(processed_data)} 条记录...")
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  第{line_num+1}行JSON解析错误: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️  第{line_num+1}行处理错误: {e}")
                    continue
    
    print(f"🎉 数据处理完成！总共处理了 {len(processed_data)} 条记录")
    
    # 统计分类信息
    category_stats = {}
    for entry in processed_data:
        cat = entry['category']
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    print(f"📊 疾病分类统计:")
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} 条")
    
    # 保存处理后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("# -*- coding: utf-8 -*-\n")
        f.write('"""\n')
        f.write("大规模医学知识库数据\n")
        f.write(f"包含 {len(processed_data)} 条医学知识条目\n")
        f.write('"""\n\n')
        f.write("LARGE_MEDICAL_KNOWLEDGE_DATABASE = ")
        f.write(json.dumps(processed_data, ensure_ascii=False, indent=2))
        f.write("\n\n")
        f.write("def get_large_medical_knowledge_count():\n")
        f.write(f'    """获取大规模医学知识条目数量"""\n')
        f.write(f"    return {len(processed_data)}\n\n")
        f.write("def get_large_medical_knowledge_by_category(category):\n")
        f.write('    """根据分类获取大规模医学知识"""\n')
        f.write("    return [item for item in LARGE_MEDICAL_KNOWLEDGE_DATABASE if item['category'] == category]\n\n")
        f.write("def get_all_large_categories():\n")
        f.write('    """获取所有大规模疾病分类"""\n')
        f.write("    return list(set(item['category'] for item in LARGE_MEDICAL_KNOWLEDGE_DATABASE))\n")
    
    print(f"💾 数据已保存到: {output_file}")
    return len(processed_data)

if __name__ == "__main__":
    # 处理数据，限制为前2000条以避免文件过大
    count = process_medical_data(
        input_file="data/medical.json",
        output_file="data/large_medical_knowledge_data.py",
        max_records=2000
    )
    print(f"🚀 大规模医疗知识库准备完成！包含 {count} 条记录")
