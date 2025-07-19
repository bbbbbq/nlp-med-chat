#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_patients_api():
    """测试患者管理API的编码问题"""
    
    base_url = "http://127.0.0.1:3000"
    
    print("🔍 测试患者管理API...")
    
    # 1. 测试获取患者列表
    try:
        print(f"🔗 正在连接: {base_url}/patients")
        response = requests.get(f"{base_url}/patients", timeout=10)
        print(f"📊 GET /patients 状态码: {response.status_code}")
        print(f"📊 响应头 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📊 原始响应内容: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 响应数据结构: {type(data)}")
            print(f"📊 成功状态: {data.get('success', 'N/A')}")
            
            patients = data.get('patients', [])
            print(f"📊 患者数量: {len(patients)}")
            
            if patients:
                print("📊 第一个患者数据:")
                first_patient = patients[0]
                for key, value in first_patient.items():
                    print(f"   {key}: {value} (类型: {type(value)})")
                    # 检查是否有编码问题
                    if isinstance(value, str):
                        try:
                            # 尝试编码/解码测试
                            encoded = value.encode('utf-8')
                            decoded = encoded.decode('utf-8')
                            print(f"   {key} UTF-8编码测试: ✅ 正常")
                        except UnicodeError as e:
                            print(f"   {key} UTF-8编码测试: ❌ 错误 - {e}")
            else:
                print("📊 没有患者数据")
                
        else:
            print(f"❌ API调用失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 2. 测试添加患者（包含中文）
    print("\n🔍 测试添加患者...")
    test_patient = {
        "name": "测试患者",
        "age": 30,
        "gender": "男",
        "contact_info": "13800138000"
    }
    
    try:
        response = requests.post(f"{base_url}/patients", json=test_patient)
        print(f"📊 POST /patients 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 添加结果: {data}")
        else:
            print(f"❌ 添加失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 添加患者异常: {e}")

if __name__ == "__main__":
    test_patients_api()
