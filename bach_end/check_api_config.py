#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_api_config():
    """检查API配置"""
    
    try:
        import config
        
        print("🔍 检查API配置...")
        
        # 检查API_TOKEN是否存在
        if hasattr(config, 'API_TOKEN'):
            token = config.API_TOKEN
            if token:
                print(f"✅ API_TOKEN已配置 (长度: {len(token)} 字符)")
                print(f"   前缀: {token[:10]}...")
            else:
                print("❌ API_TOKEN为空")
        else:
            print("❌ 未找到API_TOKEN配置")
            
        # 检查其他可能的配置
        print("\n📋 config.py中的所有属性:")
        for attr in dir(config):
            if not attr.startswith('_'):
                value = getattr(config, attr)
                if isinstance(value, str) and len(value) > 20:
                    print(f"   {attr}: {value[:10]}... (长度: {len(value)})")
                else:
                    print(f"   {attr}: {value}")
                    
    except ImportError as e:
        print(f"❌ 无法导入config模块: {e}")
    except Exception as e:
        print(f"❌ 检查配置时出错: {e}")

if __name__ == "__main__":
    check_api_config()
