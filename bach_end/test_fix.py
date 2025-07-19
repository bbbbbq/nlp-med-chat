#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_patients_fix():
    """测试患者管理页面修复效果"""
    
    try:
        print("🔍 测试患者管理API修复效果...")
        
        # 测试获取患者列表
        response = requests.get('http://127.0.0.1:3000/patients', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            patients = data.get('patients', [])
            
            print(f"✅ API调用成功，获取到 {len(patients)} 个患者")
            
            if patients:
                print("📊 前3个患者信息:")
                for i, patient in enumerate(patients[:3], 1):
                    print(f"   {i}. 姓名: {patient.get('name', 'N/A')}")
                    print(f"      性别: {patient.get('gender', 'N/A')}")
                    print(f"      年龄: {patient.get('age', 'N/A')}")
                    print(f"      联系方式: {patient.get('contact_info', 'N/A')}")
                    print()
                
                # 检查是否还有乱码
                first_patient = patients[0]
                name = first_patient.get('name', '')
                gender = first_patient.get('gender', '')
                
                if '\\u' in str(name) or '\\u' in str(gender):
                    print("⚠️  仍然存在Unicode转义字符")
                elif any(ord(c) > 127 for c in name + gender):
                    print("✅ 中文字符显示正常")
                else:
                    print("ℹ️  数据为英文或数字")
                    
            else:
                print("📭 没有患者数据")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_patients_fix()
