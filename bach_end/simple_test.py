#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试优化后的诊断API
"""

import requests
import json

def test_diagnosis_api():
    """直接测试诊断API"""
    url = "http://86f3e642154b475c98092f118c62c793.qhdcloud.lanyun.net:10240/v1/chat/completions"
    headers = {
        "Authorization": "Bearer test-key",
        "Content-Type": "application/json"
    }
    
    # 测试提示词
    prompt = """
作为专业医疗AI助手，基于以下症状信息提供简洁的诊断建议：

症状信息：
【影像类型】：胸部X光片
【观察到的症状】：
1. 双肺纹理增粗
2. 右下肺野可见片状阴影
3. 肺门结构清晰
【异常区域】：右下肺野
【严重程度】：中等

请严格按以下格式回复（保持简洁）：

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

请保持回答简洁专业，避免重复内容。
"""
    
    # 优化后的参数
    data = {
        "model": "lanyun",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.3,
        "top_p": 0.9,
        "frequency_penalty": 0.6,
        "presence_penalty": 0.3,
        "stop": ["参考资料：", "《", "祝您"]
    }
    
    print("🧪 测试优化后的诊断API参数...")
    print(f"📤 发送请求到: {url}")
    print(f"🤖 使用模型:lanyun")
    print(f"🎛️ 参数: temperature=0.3, top_p=0.9, frequency_penalty=0.6")
    print("="*60)
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print("✅ API调用成功!")
            print("="*60)
            print("📋 诊断结果:")
            print(content)
            print("="*60)
            
            # 分析结果质量
            print("📊 结果分析:")
            print(f"• 内容长度: {len(content)} 字符")
            
            if "《中华结核和呼吸杂志》" in content:
                print("⚠️  检测到重复的参考资料")
            else:
                print("✅ 未检测到重复内容")
                
            if len(content) > 2000:
                print("⚠️  输出较长，可能包含冗余信息")
            else:
                print("✅ 输出长度合理")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_diagnosis_api()
