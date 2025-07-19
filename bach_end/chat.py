

import requests
import config
import time
from rag import initialize_medical_rag, MedicalRAGRetriever
from logger_config import log_info, log_error, log_api_call, log_rag_operation, log_user_interaction


def upload_image(image_bytes: bytes, filename: str = 'image.png', max_retries: int = 3):
    """
    Uploads an image to SM.MS and returns the URL.

    :param image_bytes: The raw bytes of the image to upload.
    :param filename: The filename to use for the uploaded image.
    :param max_retries: Maximum number of retry attempts.
    :return: The URL of the uploaded image, or None if the upload fails.
    """
    api_url = 'https://sm.ms/api/v2/upload'
    headers = {
        # IMPORTANT: Replace with your own API token from https://sm.ms/home/apitoken
        'Authorization': config.API_TOKEN 
    }
    files = {
        'smfile': (filename, image_bytes)
    }

    for attempt in range(max_retries):
        try:
            print(f"尝试上传图片... ({attempt + 1}/{max_retries})")
            response = requests.post(api_url, headers=headers, files=files, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            result = response.json()

            if result.get('success'):
                print(f"图片上传成功: {result['data']['url']}")
                return result['data']['url']
            elif result.get('code') == 'image_repeated':
                # If the image is a duplicate, the API returns the URL of the existing image.
                print(f"图片已存在: {result['images']}")
                return result['images']
            else:
                print(f"Failed to upload image: {result.get('message')}")
                return None

        except requests.exceptions.SSLError as e:
            print(f"第{attempt + 1}次尝试 SSL 错误: {e}")
            if attempt < max_retries - 1:
                print(f"等待 {2 ** attempt} 秒后重试...")
                time.sleep(2 ** attempt)  # 指数退避
            else:
                print("所有重试均失败，SSL 连接问题")
                return None
        except requests.exceptions.RequestException as e:
            print(f"第{attempt + 1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                print(f"等待 {2 ** attempt} 秒后重试...")
                time.sleep(2 ** attempt)
            else:
                print("所有重试均失败")
                return None
    
    return None
    

class SymptomExtractor:
    """医疗影像症状提取与诊断建议生成器"""
    
    def __init__(self):
        self.medical_image_prompt = """
作为专业的医疗影像分析助手，请仔细分析这张医疗影像并提取可见的症状和异常表现。

请按以下格式回复：
【影像类型】：（如：X光片、CT、MRI、超声波等）
【观察到的症状】：
1. 症状描述1
2. 症状描述2
...
【异常区域】：描述异常的具体位置
【严重程度】：轻微/中等/严重

注意：请仅描述影像中可见的客观症状，不要给出诊断结论。
"""
        
        self.diagnosis_prompt = """
作为专业医疗AI助手，基于以下症状信息提供简洁的诊断建议：

症状信息：
{symptoms}

请严格按以下格式回复（保持简洁，避免任何重复内容）：

【可能诊断】：
1. 诊断1（概率：高/中/低）
2. 诊断2（概率：高/中/低）
3. 诊断3（概率：高/中/低）

【建议检查】：
• 检查项目1
• 检查项目2
• 检查项目3

【处理建议】：
• 治疗建议1
• 治疗建议2
• 生活建议

【注意事项】：
本分析仅供参考，请务必咨询专业医生确诊。如症状加重请及时就医。

重要提醒：
1. 请严格按照上述格式输出，不要添加任何额外内容
2. 绝对不要重复任何文字或段落
3. 注意事项部分只需要简短的一句话即可
4. 回答完毕后立即停止，不要继续生成内容
"""
        
        # 初始化RAG系统
        print("🔄 正在初始化医学RAG系统...")
        log_info("开始初始化医学RAG系统")
        try:
            self.knowledge_base, self.rag_retriever = initialize_medical_rag()
            print("✅ RAG系统初始化成功")
            log_info("RAG系统初始化成功")
        except Exception as e:
            print(f"⚠️ RAG系统初始化失败: {e}")
            log_error(f"RAG系统初始化失败: {e}", exc_info=True)
            self.knowledge_base = None
            self.rag_retriever = None
    
    def chat_with_gpt(self, prompt, img_url=None, use_reasoner=False):
        """调用DeepSeek API（用于第一步：症状提取）"""
        api_key = config.DEEPSEEK_API_KEY
        # 根据是否需要推理能力和是否有图片选择模型
        if img_url:
            model = "deepseek-chat"  # 图片分析使用deepseek-chat
        else:
            model = "deepseek-reasoner" if use_reasoner else "deepseek-chat"
            
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构造内容 - 使用简单的图片标签格式
        if img_url:
            content = f"<image>{img_url}</image>\n{prompt}"
        else:
            content = prompt
            
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 2048 if use_reasoner else 1024,
            "temperature": 0.1
        }
        
        print(f"📤 [第一步] 发送API请求到: {url}")
        print(f"🤖 使用模型: {model}")
        print(f"📝 内容长度: {len(str(content))} 字符")
        
        # 记录API调用开始
        start_time = time.time()
        log_api_call("POST", url, status_code=None)
        
        response = requests.post(url, headers=headers, json=data)
        response_time = time.time() - start_time
        
        print(f"📶 API响应 - 模型: {model}, 状态: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            print(f"✅ [第一步] API调用成功，返回内容长度: {len(content)} 字符")
            
            # 记录成功API调用
            log_api_call("POST", url, response.status_code, response_time)
            
            # 如果有reasoning_content，也一并返回
            if 'reasoning_content' in response_data['choices'][0]['message']:
                reasoning = response_data['choices'][0]['message']['reasoning_content']
                print(f"🧠 推理过程长度: {len(reasoning)} 字符")
            return content
        else:
            error_msg = f"API调用失败: {response.status_code} - {response.text}"
            print(f"❌ [第一步] {error_msg}")
            log_api_call("POST", url, response.status_code, response_time, error_msg)
            return f"抱歉，症状提取失败: {error_msg}"
    
    def chat_with_diagnosis_api(self, prompt):
        """调用新的诊断API（用于第二步：诊断建议生成）"""
        url = "http://86f3e642154b475c98092f118c62c793.qhdcloud.lanyun.net:10240/v1/chat/completions"
        headers = {
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mine",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 800,   # 进一步减少最大token数，避免冗余内容
            "temperature": 0.1,   # 降低温度，提高确定性，减少重复
            "top_p": 0.8,        # 核采样，提高输出质量
            "frequency_penalty": 1.0,  # 最大频率惩罚，强力减少重复
            "presence_penalty": 0.8,   # 高存在惩罚，鼓励多样性
            "stop": ["参考资料：", "《", "祝您", "本平台", "以上信息", "如有疑问", "本分析仅供参考", "请务必咨询"]  # 更多停止词，避免重复免责声明
        }
        
        print(f"📤 [第二步] 发送诊断API请求到: {url}")
        print(f"🤖 使用诊断模型: gpt-3.5-turbo")
        print(f"📝 内容长度: {len(str(prompt))} 字符")
        
        # 记录API调用开始
        start_time = time.time()
        log_api_call("POST", url, status_code=None)
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=180)
            response_time = time.time() - start_time
            
            print(f"📶 诊断API响应 - 状态: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                print(f"✅ [第二步] 诊断API调用成功，返回内容长度: {len(content)} 字符")
                
                # 记录成功API调用
                log_api_call("POST", url, response.status_code, response_time)
                
                return content
            else:
                error_msg = f"诊断API调用失败: {response.status_code} - {response.text}"
                print(f"❌ [第二步] {error_msg}")
                log_api_call("POST", url, response.status_code, response_time, error_msg)
                return f"抱歉，诊断建议生成失败: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            error_msg = f"诊断API请求异常: {str(e)}"
            print(f"❌ [第二步] {error_msg}")
            log_api_call("POST", url, 0, response_time, error_msg)
            return f"抱歉，诊断API连接失败: {str(e)}"
    
    def extract_symptoms_from_image(self, img_url):
        """第一步：从医疗影像中提取症状"""
        print("🔍 第一步：分析医疗影像，提取症状...")
        return self.chat_with_gpt(self.medical_image_prompt, img_url)
    
    def generate_diagnosis_advice(self, symptoms):
        """第二步：根据症状生成诊断建议（RAG增强版）"""
        print("🩺 第二步：基于症状生成诊断建议...")
        
        # 使用RAG检索相关医学知识并检查匹配度
        use_rag = False
        relevant_knowledge = ""
        max_relevance_score = 0.0
        
        if self.rag_retriever:
            try:
                print("📚 正在检索相关医学知识...")
                # 直接调用知识库的搜索方法获取详细的匹配度信息
                knowledge_results = self.knowledge_base.search_relevant_knowledge(symptoms, top_k=3)
                
                if knowledge_results:
                    # 获取最高匹配度
                    max_relevance_score = max([k['relevance_score'] for k in knowledge_results])
                    print(f"📊 最高匹配度: {max_relevance_score:.3f}")
                    
                    # 记录RAG检索结果
                    log_rag_operation("知识检索", f"症状匹配", max_relevance_score, len(knowledge_results))
                    
                    # 只有当匹配度超过0.7时才使用RAG
                    if max_relevance_score > 0.7:
                        use_rag = True
                        relevant_knowledge = self.rag_retriever.retrieve_and_format(symptoms, top_k=3)
                        print(f"✅ 匹配度 {max_relevance_score:.3f} > 0.7，使用RAG增强诊断")
                        log_rag_operation("RAG增强诊断", "匹配度超过阈值", max_relevance_score)
                    else:
                        print(f"⚠️ 匹配度 {max_relevance_score:.3f} ≤ 0.7，使用传统诊断方式")
                        log_rag_operation("传统诊断", "匹配度未达阈值", max_relevance_score)
                else:
                    print("📚 未找到相关医学知识")
                    
            except Exception as e:
                print(f"⚠️ RAG检索失败，使用传统方式: {e}")
        
        # 根据匹配度决定使用哪种诊断方式
        if use_rag and relevant_knowledge:
            print("🤖 正在生成RAG增强的诊断建议...")
            enhanced_prompt = f"""
基于以下从医疗影像中提取的症状信息和相关医学知识，请提供专业的诊断建议：

**症状信息：**
{symptoms}

{relevant_knowledge}

**请基于症状和医学知识参考，严格按以下格式提供诊断建议（避免任何重复内容）：**

【可能诊断】：
1. 诊断可能性1（概率：高/中/低）- 基于知识库匹配度 {max_relevance_score:.3f}
2. 诊断可能性2（概率：高/中/低）
3. 诊断可能性3（概率：高/中/低）

【建议检查】：
• 建议的进一步检查项目1
• 建议的进一步检查项目2
• 建议的进一步检查项目3

【处理建议】：
• 即时处理措施
• 后续随访建议
• 生活注意事项

【知识库匹配分析】：
症状与知识库匹配度: {max_relevance_score:.3f}，基于医学知识库提供上述建议。

【注意事项】：
此分析基于医学知识库和AI推理，仅供参考，请务必咨询专业医生进行确诊。

重要提醒：
1. 严格按照上述格式输出，不要添加任何额外内容
2. 绝对不要重复任何文字或段落
3. 回答完毕后立即停止，不要继续生成内容
"""
        else:
            # 使用传统诊断方式
            print("🤖 正在生成传统诊断建议...")
            enhanced_prompt = self.diagnosis_prompt.format(symptoms=symptoms)
            if max_relevance_score > 0:
                enhanced_prompt += f"\n\n注：已检索医学知识库，但最高匹配度仅为 {max_relevance_score:.3f}，未达到使用阈值(0.7)。"
        
        return self.chat_with_diagnosis_api(enhanced_prompt)
    
    def chat_top(self, prompt, image_bytes):
        """医疗AI两步工作流程：症状提取 → 诊断建议"""
        print("🎯 开始医疗AI两步工作流程...")
        log_user_interaction(action="医疗影像分析", details=f"提示词长度: {len(prompt)}字符")
        
        # 上传图片
        img_url = upload_image(image_bytes)
        print("img_url:", img_url)
        
        # 检查图片上传是否成功
        if img_url is None:
            return "图片上传失败，无法处理图片。请稍后重试或检查网络连接。"
        
        try:
            # 第一步：从医疗影像提取症状
            symptoms = self.extract_symptoms_from_image(img_url)
            
            # 第二步：基于症状生成诊断建议
            diagnosis = self.generate_diagnosis_advice(symptoms)
            
            # 组合最终回复
            final_response = f"""
═══════════════════════════════════════
🏥 医疗影像智能分析报告
═══════════════════════════════════════

📋 **第一步：症状提取分析**
{symptoms}

═══════════════════════════════════════

🩺 **第二步：诊断建议**
{diagnosis}

═══════════════════════════════════════
⚠️  **重要提醒**：此分析结果仅供参考，不能替代专业医生的诊断。如有健康问题，请及时就医。
"""
            
            return final_response
            
        except Exception as e:
            return f"分析过程中出现错误：{str(e)}。请稍后重试。"
    
    def generate_case_report(self, patient_data, image_attachments=None):
        """基于患者信息生成病例报告"""
        print("📊 开始处理病例生成请求...")
        print(f"患者数据: {patient_data}")
        
        # 处理图片附件
        if image_attachments:
            print(f"📎 收到 {len(image_attachments)} 个图片附件")
            for i, img in enumerate(image_attachments):
                print(f"图片 {i+1}: {img.get('filename', 'unknown')} ({img.get('size', 0)} bytes)")
        
        # 构建病历管理信息
        case_header_info = []
        name = patient_data.get('name', '')
        medical_record_number = patient_data.get('medicalRecordNumber', '')
        visit_date = patient_data.get('visitDate', '')
        report_date = patient_data.get('reportDate', '')
        reporting_physician = patient_data.get('reportingPhysician', '')
        
        # 构建患者基本信息字符串
        patient_info = []
        if name:
            patient_info.append(f"姓名：{name}")
        if patient_data.get('age'):
            patient_info.append(f"年龄：{patient_data['age']}岁")
        if patient_data.get('gender'):
            patient_info.append(f"性别：{patient_data['gender']}")
        
        patient_info_str = "，".join(patient_info) if patient_info else "基本信息未提供"
        print(f"构建的患者信息: {patient_info_str}")
        
        # 构建病历管理信息显示
        header_info = f"""**病历管理信息**
姓名： {name if name else '[需填写]'}
病历号： {medical_record_number if medical_record_number else '[需填写]'}
就诊日期： {visit_date if visit_date else '[需填写]'}
报告日期： {report_date if report_date else '[需填写]'}
报告医师： {reporting_physician if reporting_physician else '[需填写]'}"""
        
        # 构建病例生成提示词
        prompt = f"""作为一名专业的医生，请根据以下患者信息生成一份详细的病例报告。

重要要求：
1. 请直接在报告开头使用以下病历管理信息，不要修改任何已提供的具体数据
2. 对于未提供的信息，保持"[需填写]"
3. 请严格按照提供的格式生成报告

{header_info}

**患者基本信息：**
{patient_info_str}

**主诉：**
{patient_data.get('chiefComplaint', '未提供')}

**现病史：**
{patient_data.get('presentIllness', '未提供')}

**既往史：**
{patient_data.get('pastHistory', '无特殊')}

**体格检查：**
{patient_data.get('physicalExam', '未进行')}

请生成一份专业的病例报告，按以下结构组织：

1. **病历管理信息** - 使用提供的具体值，如果没有提供则保留"[\u9700\u586b\u5199]"
2. **患者基本信息** - 使用提供的姓名、年龄、性别
3. **主诉**
4. **现病史**
5. **既往史**
6. **体格检查**
7. **初步诊断**
8. **诊疗计划**
9. **预后**
10. **注意事项**

特别注意：
- 在"患者基本信息"部分，如果提供了姓名，请使用具体的姓名而不是"[\u9700\u586b\u5199]"
- 保持专业医学术语和严谨态度
- 在报告末尾添加医疗免责声明"""
        
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"提示词预览: {prompt[:200]}...")
        
        # 使用诊断API生成病例报告
        print("🤖 调用诊断API生成病例报告...")
        case_report = self.chat_with_diagnosis_api(prompt)
        
        # 在病例报告末尾添加图片附件信息
        if image_attachments and len(image_attachments) > 0:
            attachments_info = "\n\n**相关医学影像资料：**\n\n"
            for i, img in enumerate(image_attachments):
                filename = img.get('filename', f'图片{i+1}')
                size = img.get('size', 0)
                upload_time = img.get('upload_time', '未知时间')
                data_url = img.get('data_url', '')
                file_type = img.get('file_type', 'image')
                
                attachments_info += f"### {i+1}. {filename}\n\n"
                
                # 嵌入base64图片
                if data_url:
                    attachments_info += f"<img src=\"{data_url}\" alt=\"{filename}\" style=\"max-width: 500px; height: auto; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0;\">\n\n"
                
                # 添加图片信息
                attachments_info += f"**文件信息：**\n"
                attachments_info += f"- 文件名：{filename}\n"
                attachments_info += f"- 文件大小：{size:,} bytes ({size/1024:.1f} KB)\n"
                attachments_info += f"- 文件类型：{file_type.upper()}\n"
                attachments_info += f"- 上传时间：{upload_time}\n\n"
                attachments_info += "---\n\n"
            
            case_report += attachments_info
            print(f"📎 已嵌入 {len(image_attachments)} 个图片附件到病例报告")
        
        print(f"✅ 病例报告生成完成，总长度: {len(case_report)} 字符")
        print(f"报告预览: {case_report[:300]}...")
        
        return case_report