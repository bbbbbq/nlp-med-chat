#!/usr/bin/env python3
"""
大规模医学知识库数据
包含常见疾病、症状、诊断标准、治疗方案等医学知识
"""

# 大规模医学知识库数据
MEDICAL_KNOWLEDGE_DATABASE = [
    # 呼吸系统疾病
    {
        "id": "pneumonia_001",
        "category": "呼吸系统疾病",
        "disease": "肺炎",
        "symptoms": ["咳嗽", "发热", "胸痛", "呼吸困难", "痰液增多", "乏力", "食欲不振"],
        "imaging_findings": ["肺部阴影", "实变", "磨玻璃影", "胸腔积液", "肺纹理增粗"],
        "diagnosis_criteria": "临床症状 + 胸部影像学检查 + 血常规 + 痰培养",
        "treatment": "抗生素治疗、支持治疗、氧疗",
        "severity": ["轻度", "中度", "重度", "危重"],
        "content": "肺炎是肺实质的急性感染性炎症，主要表现为发热、咳嗽、胸痛等症状，胸部影像可见肺部阴影。"
    },
    {
        "id": "copd_001",
        "category": "呼吸系统疾病",
        "disease": "慢性阻塞性肺疾病",
        "symptoms": ["慢性咳嗽", "咳痰", "呼吸困难", "胸闷", "活动耐力下降"],
        "imaging_findings": ["肺气肿", "肺纹理增粗", "膈肌低平", "肺大泡"],
        "diagnosis_criteria": "肺功能检查 + 临床症状 + 影像学检查",
        "treatment": "支气管扩张剂、糖皮质激素、氧疗、肺康复",
        "severity": ["轻度", "中度", "重度", "极重度"],
        "content": "COPD是以持续气流受限为特征的疾病，气流受限呈进行性发展，与气道和肺对有害颗粒或气体的慢性炎症反应增强有关。"
    },
    {
        "id": "asthma_001",
        "category": "呼吸系统疾病",
        "disease": "支气管哮喘",
        "symptoms": ["反复喘息", "气急", "胸闷", "咳嗽", "夜间或清晨发作"],
        "imaging_findings": ["肺纹理增粗", "肺过度充气", "正常或轻度异常"],
        "diagnosis_criteria": "临床症状 + 肺功能检查 + 支气管激发试验",
        "treatment": "吸入性糖皮质激素、支气管扩张剂、避免过敏原",
        "severity": ["间歇性", "轻度持续", "中度持续", "重度持续"],
        "content": "哮喘是由多种细胞和细胞组分参与的气道慢性炎症性疾病，以可逆性气流受限为特征。"
    },
    
    # 心血管系统疾病
    {
        "id": "hypertension_001",
        "category": "心血管疾病",
        "disease": "高血压",
        "symptoms": ["头痛", "头晕", "心悸", "胸闷", "视物模糊", "耳鸣"],
        "imaging_findings": ["左心室肥厚", "主动脉扩张", "眼底动脉硬化", "心脏扩大"],
        "diagnosis_criteria": "血压测量 ≥140/90mmHg（非同日3次）",
        "treatment": "生活方式干预、ACEI/ARB、利尿剂、钙通道阻滞剂",
        "severity": ["1级", "2级", "3级"],
        "content": "高血压是以动脉血压持续升高为特征的疾病，可导致心、脑、肾等器官损害。"
    },
    {
        "id": "coronary_heart_disease_001",
        "category": "心血管疾病",
        "disease": "冠心病",
        "symptoms": ["胸痛", "胸闷", "气短", "心悸", "乏力", "活动后症状加重"],
        "imaging_findings": ["冠脉狭窄", "心肌缺血", "室壁运动异常", "钙化斑块"],
        "diagnosis_criteria": "心电图 + 冠脉造影 + 心肌酶 + 临床症状",
        "treatment": "抗血小板、他汀类药物、硝酸酯类、介入治疗",
        "severity": ["稳定型", "不稳定型", "急性心梗"],
        "content": "冠心病是冠状动脉粥样硬化导致血管狭窄或闭塞，引起心肌缺血缺氧的疾病。"
    },
    {
        "id": "heart_failure_001",
        "category": "心血管疾病",
        "disease": "心力衰竭",
        "symptoms": ["呼吸困难", "乏力", "下肢水肿", "夜间阵发性呼吸困难"],
        "imaging_findings": ["心脏扩大", "肺淤血", "胸腔积液", "射血分数降低"],
        "diagnosis_criteria": "超声心动图 + BNP/NT-proBNP + 临床症状",
        "treatment": "ACEI/ARB、β受体阻滞剂、利尿剂、强心药",
        "severity": ["I级", "II级", "III级", "IV级"],
        "content": "心力衰竭是心脏结构或功能异常导致心室充盈或射血能力受损的临床综合征。"
    },
    
    # 消化系统疾病
    {
        "id": "gastritis_001",
        "category": "消化系统疾病",
        "disease": "胃炎",
        "symptoms": ["上腹痛", "恶心", "呕吐", "食欲不振", "腹胀", "反酸"],
        "imaging_findings": ["胃壁增厚", "粘膜糜烂", "溃疡形成", "胃窦炎症"],
        "diagnosis_criteria": "临床症状 + 胃镜检查 + 病理活检 + 幽门螺杆菌检测",
        "treatment": "抑酸治疗、根除幽门螺杆菌、保护胃粘膜、饮食调节",
        "severity": ["轻度", "中度", "重度"],
        "content": "胃炎是胃粘膜炎症性疾病，主要症状为上腹痛、恶心等，需要胃镜确诊。"
    },
    {
        "id": "peptic_ulcer_001",
        "category": "消化系统疾病",
        "disease": "消化性溃疡",
        "symptoms": ["上腹痛", "饥饿痛", "夜间痛", "反酸", "嗳气", "黑便"],
        "imaging_findings": ["溃疡龛影", "粘膜缺损", "瘢痕形成", "十二指肠变形"],
        "diagnosis_criteria": "胃镜检查 + 临床症状 + 幽门螺杆菌检测",
        "treatment": "质子泵抑制剂、根除HP、保护粘膜、避免刺激性食物",
        "severity": ["活动期", "愈合期", "瘢痕期"],
        "content": "消化性溃疡是胃酸和胃蛋白酶对粘膜自身消化所形成的溃疡，好发于胃和十二指肠。"
    },
    {
        "id": "hepatitis_001",
        "category": "消化系统疾病",
        "disease": "病毒性肝炎",
        "symptoms": ["乏力", "食欲不振", "恶心", "腹胀", "肝区疼痛", "黄疸"],
        "imaging_findings": ["肝脏肿大", "肝实质回声增强", "脾脏肿大", "腹水"],
        "diagnosis_criteria": "肝功能检查 + 病毒标志物 + 临床症状",
        "treatment": "抗病毒治疗、保肝治疗、对症支持治疗",
        "severity": ["轻度", "中度", "重度", "重型"],
        "content": "病毒性肝炎是由肝炎病毒感染引起的肝脏炎症，主要有甲、乙、丙、丁、戊型。"
    },
    
    # 神经系统疾病
    {
        "id": "stroke_001",
        "category": "神经系统疾病",
        "disease": "脑卒中",
        "symptoms": ["偏瘫", "失语", "面瘫", "头痛", "意识障碍", "眩晕"],
        "imaging_findings": ["脑梗死灶", "脑出血", "脑水肿", "中线移位", "血管闭塞"],
        "diagnosis_criteria": "临床症状 + CT/MRI检查 + 血管造影",
        "treatment": "溶栓治疗、抗血小板、神经保护、康复训练",
        "severity": ["轻型", "中型", "重型"],
        "content": "脑卒中包括缺血性和出血性两种类型，需要紧急诊治以减少后遗症。"
    },
    {
        "id": "epilepsy_001",
        "category": "神经系统疾病",
        "disease": "癫痫",
        "symptoms": ["抽搐", "意识丧失", "口吐白沫", "大小便失禁", "先兆症状"],
        "imaging_findings": ["脑电图异常", "海马硬化", "皮质发育不良", "肿瘤"],
        "diagnosis_criteria": "脑电图 + 临床发作表现 + 影像学检查",
        "treatment": "抗癫痫药物、手术治疗、生酮饮食",
        "severity": ["局灶性", "全面性", "难治性"],
        "content": "癫痫是大脑神经元异常放电引起的慢性疾病，表现为反复发作的抽搐或意识障碍。"
    },
    {
        "id": "parkinsons_001",
        "category": "神经系统疾病",
        "disease": "帕金森病",
        "symptoms": ["静止性震颤", "肌强直", "运动迟缓", "姿势步态异常"],
        "imaging_findings": ["黑质变性", "多巴胺转运体显像异常", "脑萎缩"],
        "diagnosis_criteria": "临床症状 + 左旋多巴试验 + DaTSCAN",
        "treatment": "左旋多巴、多巴胺受体激动剂、深部脑刺激",
        "severity": ["早期", "中期", "晚期"],
        "content": "帕金森病是黑质多巴胺能神经元变性导致的运动障碍疾病。"
    },
    
    # 内分泌系统疾病
    {
        "id": "diabetes_001",
        "category": "内分泌疾病",
        "disease": "糖尿病",
        "symptoms": ["多饮", "多尿", "多食", "体重下降", "乏力", "视力模糊"],
        "imaging_findings": ["糖尿病视网膜病变", "糖尿病肾病", "血管病变"],
        "diagnosis_criteria": "空腹血糖≥7.0mmol/L或餐后2h血糖≥11.1mmol/L",
        "treatment": "饮食控制、运动、口服降糖药、胰岛素",
        "severity": ["1型", "2型", "妊娠期", "特殊类型"],
        "content": "糖尿病是胰岛素分泌缺陷或作用障碍引起的代谢性疾病，以高血糖为特征。"
    },
    {
        "id": "hyperthyroidism_001",
        "category": "内分泌疾病",
        "disease": "甲状腺功能亢进",
        "symptoms": ["心悸", "多汗", "体重下降", "易激动", "手抖", "怕热"],
        "imaging_findings": ["甲状腺肿大", "血流增加", "结节", "突眼"],
        "diagnosis_criteria": "甲状腺功能检查 + 临床症状 + 甲状腺超声",
        "treatment": "抗甲状腺药物、放射性碘治疗、手术治疗",
        "severity": ["轻度", "中度", "重度"],
        "content": "甲亢是甲状腺激素分泌过多引起的临床综合征，以代谢亢进为主要表现。"
    },
    
    # 泌尿系统疾病
    {
        "id": "kidney_stone_001",
        "category": "泌尿系统疾病",
        "disease": "肾结石",
        "symptoms": ["腰痛", "血尿", "恶心呕吐", "尿频", "尿急", "排尿困难"],
        "imaging_findings": ["肾盂积水", "结石影", "输尿管扩张", "肾实质变薄"],
        "diagnosis_criteria": "CT检查 + 临床症状 + 尿常规",
        "treatment": "多饮水、药物排石、体外碎石、手术取石",
        "severity": ["小结石", "中等结石", "大结石"],
        "content": "肾结石是尿液中晶体物质异常聚积形成的固体块状物，可引起剧烈疼痛。"
    },
    {
        "id": "uti_001",
        "category": "泌尿系统疾病",
        "disease": "尿路感染",
        "symptoms": ["尿频", "尿急", "尿痛", "血尿", "下腹痛", "发热"],
        "imaging_findings": ["膀胱壁增厚", "肾盂积水", "肾脏肿胀"],
        "diagnosis_criteria": "尿常规 + 尿培养 + 临床症状",
        "treatment": "抗生素治疗、多饮水、对症治疗",
        "severity": ["下尿路感染", "上尿路感染", "复杂性感染"],
        "content": "尿路感染是病原体在尿路中生长繁殖并侵犯尿路粘膜或组织引起的炎症。"
    },
    
    # 骨科疾病
    {
        "id": "fracture_001",
        "category": "骨科疾病",
        "disease": "骨折",
        "symptoms": ["疼痛", "肿胀", "功能障碍", "畸形", "异常活动"],
        "imaging_findings": ["骨质连续性中断", "骨折线", "移位", "碎骨片"],
        "diagnosis_criteria": "外伤史 + 临床症状 + X线检查",
        "treatment": "复位、固定、功能锻炼",
        "severity": ["无移位", "有移位", "粉碎性", "开放性"],
        "content": "骨折是骨质连续性中断，X线可见骨折线，需要根据移位情况选择保守或手术治疗。"
    },
    {
        "id": "arthritis_001",
        "category": "骨科疾病",
        "disease": "关节炎",
        "symptoms": ["关节疼痛", "肿胀", "僵硬", "活动受限", "晨僵"],
        "imaging_findings": ["关节间隙狭窄", "骨质增生", "软骨破坏", "关节积液"],
        "diagnosis_criteria": "临床症状 + X线检查 + 实验室检查",
        "treatment": "非甾体抗炎药、关节腔注射、物理治疗",
        "severity": ["轻度", "中度", "重度"],
        "content": "关节炎是关节软骨和周围组织的炎症性疾病，可导致关节疼痛和功能障碍。"
    },
    
    # 外科疾病
    {
        "id": "appendicitis_001",
        "category": "外科疾病",
        "disease": "急性阑尾炎",
        "symptoms": ["右下腹痛", "发热", "恶心呕吐", "腹肌紧张", "反跳痛"],
        "imaging_findings": ["阑尾壁增厚", "周围渗出", "腹腔积液", "阑尾结石"],
        "diagnosis_criteria": "临床症状 + 腹部CT + 血常规",
        "treatment": "阑尾切除术、抗生素治疗",
        "severity": ["单纯性", "化脓性", "坏疽性", "穿孔性"],
        "content": "急性阑尾炎是阑尾的急性炎症，典型表现为转移性右下腹痛，需要手术治疗。"
    },
    {
        "id": "gallstone_001",
        "category": "外科疾病",
        "disease": "胆石症",
        "symptoms": ["右上腹痛", "恶心呕吐", "黄疸", "发热", "腹胀"],
        "imaging_findings": ["胆囊结石", "胆囊壁增厚", "胆管扩张", "胆泥"],
        "diagnosis_criteria": "腹部超声 + 临床症状 + 肝功能检查",
        "treatment": "腹腔镜胆囊切除、药物溶石、体外碎石",
        "severity": ["无症状", "有症状", "并发症"],
        "content": "胆石症是胆道系统结石形成的疾病，可引起胆绞痛和胆道感染。"
    },
    
    # 妇科疾病
    {
        "id": "ovarian_cyst_001",
        "category": "妇科疾病",
        "disease": "卵巢囊肿",
        "symptoms": ["下腹痛", "腹胀", "月经不调", "尿频", "便秘"],
        "imaging_findings": ["卵巢囊性占位", "囊壁厚薄不均", "分隔", "实性成分"],
        "diagnosis_criteria": "妇科检查 + 超声检查 + 肿瘤标志物",
        "treatment": "观察随访、药物治疗、手术切除",
        "severity": ["功能性", "病理性", "恶性"],
        "content": "卵巢囊肿是卵巢内或表面形成的囊性肿物，多数为良性。"
    },
    {
        "id": "endometriosis_001",
        "category": "妇科疾病",
        "disease": "子宫内膜异位症",
        "symptoms": ["痛经", "慢性盆腔痛", "性交痛", "不孕", "月经异常"],
        "imaging_findings": ["卵巢巧克力囊肿", "子宫腺肌症", "盆腔粘连"],
        "diagnosis_criteria": "临床症状 + 影像学检查 + 腹腔镜检查",
        "treatment": "药物治疗、手术治疗、辅助生殖技术",
        "severity": ["I期", "II期", "III期", "IV期"],
        "content": "子宫内膜异位症是子宫内膜组织出现在子宫体以外部位的疾病。"
    },
    
    # 皮肤科疾病
    {
        "id": "eczema_001",
        "category": "皮肤科疾病",
        "disease": "湿疹",
        "symptoms": ["皮肤瘙痒", "红斑", "丘疹", "水疱", "糜烂", "结痂"],
        "imaging_findings": ["皮肤增厚", "色素沉着", "抓痕", "继发感染"],
        "diagnosis_criteria": "临床表现 + 病史 + 过敏原检测",
        "treatment": "外用糖皮质激素、抗组胺药、保湿剂",
        "severity": ["轻度", "中度", "重度"],
        "content": "湿疹是一种常见的过敏性皮肤病，以皮肤瘙痒和炎症为主要特征。"
    },
    {
        "id": "psoriasis_001",
        "category": "皮肤科疾病",
        "disease": "银屑病",
        "symptoms": ["红斑", "鳞屑", "瘙痒", "关节疼痛", "指甲改变"],
        "imaging_findings": ["典型皮损", "点状出血", "薄膜现象", "关节破坏"],
        "diagnosis_criteria": "临床表现 + 皮肤活检 + 家族史",
        "treatment": "外用药物、光疗、系统治疗、生物制剂",
        "severity": ["轻度", "中度", "重度"],
        "content": "银屑病是一种慢性炎症性皮肤病，以红斑鳞屑为主要表现。"
    }
]

def get_medical_knowledge_count():
    """获取医学知识条目数量"""
    return len(MEDICAL_KNOWLEDGE_DATABASE)

def get_medical_knowledge_by_category(category):
    """根据分类获取医学知识"""
    return [item for item in MEDICAL_KNOWLEDGE_DATABASE if item['category'] == category]

def get_all_categories():
    """获取所有疾病分类"""
    return list(set(item['category'] for item in MEDICAL_KNOWLEDGE_DATABASE))
