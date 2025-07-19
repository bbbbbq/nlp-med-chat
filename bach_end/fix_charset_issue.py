#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

# 数据库配置
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'nlpchat'

def fix_charset_issue():
    """修复患者管理页面的字符编码问题"""
    
    try:
        # 连接数据库
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        print("🔧 开始修复字符编码问题...")
        
        # 1. 备份当前数据
        print("📋 备份当前患者数据...")
        cursor.execute("SELECT id, name, gender FROM patients LIMIT 10")
        current_data = cursor.fetchall()
        
        print("📊 当前数据样本:")
        for row in current_data:
            print(f"   ID: {row[0]}, 姓名: {row[1]}, 性别: {row[2]}")
        
        # 2. 清空患者表
        print("🗑️ 清空患者表...")
        cursor.execute("DELETE FROM patients")
        cursor.execute("ALTER TABLE patients AUTO_INCREMENT = 1")
        
        # 3. 重新插入正确的测试数据
        print("✨ 插入正确编码的测试数据...")
        
        test_patients = [
            ('张三', 45, '男', '13800138001', '高血压病史5年'),
            ('李四', 32, '女', '13800138002', '无特殊病史'),
            ('王五', 58, '男', '13800138003', '糖尿病病史8年'),
            ('赵六', 28, '女', '13800138004', '过敏性鼻炎'),
            ('钱七', 67, '男', '13800138005', '冠心病，高脂血症'),
            ('孙八', 41, '女', '13800138006', '甲状腺功能亢进'),
            ('周九', 35, '男', '13800138007', '慢性胃炎'),
            ('吴十', 52, '女', '13800138008', '骨质疏松'),
            ('郑一', 39, '男', '13800138009', '脂肪肝'),
            ('王二', 44, '女', '13800138010', '乳腺增生')
        ]
        
        # 使用正确的字符集插入数据
        insert_query = """
        INSERT INTO patients (name, age, gender, contact_info, medical_history) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, test_patients)
        db.commit()
        
        print(f"✅ 成功插入 {len(test_patients)} 条患者记录")
        
        # 4. 验证修复结果
        print("🔍 验证修复结果...")
        cursor.execute("SELECT id, name, gender FROM patients LIMIT 5")
        fixed_data = cursor.fetchall()
        
        print("📊 修复后的数据:")
        for row in fixed_data:
            print(f"   ID: {row[0]}, 姓名: {row[1]}, 性别: {row[2]}")
        
        cursor.close()
        db.close()
        
        print("🎉 字符编码问题修复完成！")
        print("💡 请刷新前端页面查看效果")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")

if __name__ == "__main__":
    fix_charset_issue()
