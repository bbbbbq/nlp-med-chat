#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import os

# 数据库配置（与app.py保持一致）
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'nlpchat'

def check_database_charset():
    """检查数据库字符集配置"""
    
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
        
        print("🔍 检查数据库字符集配置...")
        
        # 1. 检查数据库字符集
        cursor.execute("SELECT @@character_set_database, @@collation_database")
        db_charset = cursor.fetchone()
        print(f"📊 数据库字符集: {db_charset[0]}")
        print(f"📊 数据库排序规则: {db_charset[1]}")
        
        # 2. 检查连接字符集
        cursor.execute("SELECT @@character_set_connection, @@collation_connection")
        conn_charset = cursor.fetchone()
        print(f"📊 连接字符集: {conn_charset[0]}")
        print(f"📊 连接排序规则: {conn_charset[1]}")
        
        # 3. 检查patients表结构
        cursor.execute("SHOW CREATE TABLE patients")
        table_info = cursor.fetchone()
        print(f"📊 patients表创建语句:")
        print(table_info[1])
        
        # 4. 检查表字符集
        cursor.execute("""
            SELECT COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'patients' 
            AND CHARACTER_SET_NAME IS NOT NULL
        """, (DB_NAME,))
        
        columns = cursor.fetchall()
        print(f"📊 patients表列字符集:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({col[2]})")
        
        # 5. 检查现有数据
        cursor.execute("SELECT id, name, gender FROM patients LIMIT 3")
        patients = cursor.fetchall()
        print(f"📊 现有患者数据样本:")
        for patient in patients:
            print(f"   ID: {patient[0]}, 姓名: {patient[1]}, 性别: {patient[2]}")
            # 检查原始字节
            if isinstance(patient[1], str):
                name_bytes = patient[1].encode('latin1')
                print(f"   姓名原始字节: {name_bytes}")
                try:
                    # 尝试重新解码
                    name_utf8 = name_bytes.decode('utf8')
                    print(f"   姓名UTF-8解码: {name_utf8}")
                except:
                    print(f"   姓名UTF-8解码失败")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    check_database_charset()
