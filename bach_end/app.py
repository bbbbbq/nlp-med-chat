import os
import uuid
import base64
import boto3
import mysql.connector
from openai import OpenAI
import json
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from chat import SymptomExtractor
from datetime import datetime
import traceback
import io
import re
import markdown
from PIL import Image as PILImage
import urllib.parse
from rag import initialize_medical_rag
from logger_config import log_info, log_error, log_user_interaction, log_system_startup

# PDF生成相关导入
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    # 如果reportlab未安装，设置为None
    A4 = None
    getSampleStyleSheet = None
    ParagraphStyle = None
    inch = None
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    Image = None
    pdfmetrics = None
    TTFont = None

# --- App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# 配置Flask以确保JSON响应中的中文字符不被转义
app.config['JSON_AS_ASCII'] = False

# 全局SymptomExtractor实例，避免重复初始化RAG系统
print("🚀 正在初始化全局医疗AI系统...")
global_extractor = None

def get_symptom_extractor():
    """获取全局SymptomExtractor实例"""
    global global_extractor
    if global_extractor is None:
        print("🔄 首次初始化SymptomExtractor...")
        global_extractor = SymptomExtractor()
        print("✅ 全局SymptomExtractor初始化完成")
    return global_extractor

# --- Configurations ---
MINIO_ENDPOINT = '127.0.0.1:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET_NAME = 'caseimage'

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'nlpchat'

# DeepSeek API Configuration
# WARNING: It is strongly recommended to move the API key to an environment variable for security.
DEEPSEEK_API_KEY = 'sk-6c3a45091cd7450695a2fa1ca8c19430'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

# --- Services ---
# MinIO Client
s3_client = boto3.client(
    's3',
    endpoint_url=f'http://{MINIO_ENDPOINT}',
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=boto3.session.Config(signature_version='s3v4')
)

# Database Connection Management
def get_db_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- API Endpoints ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO doctors (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        db.commit()
        return jsonify({'success': True, 'message': '注册成功'})
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Registration failed: {err}'}), 500

        
@app.route('/login', methods=['POST'])
def login():
    print('Received login request')
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Check doctors table first
        cursor.execute("SELECT password FROM doctors WHERE username = %s", (username,))
        doctor = cursor.fetchone()
        print(f'Checking doctor {username}')
        if doctor:
            if doctor['password'] == password:
                return jsonify({'success': True, 'message': 'Login successful', 'role': 'doctor'})
        
        # If not a doctor, check admins table
        cursor.execute("SELECT password FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        print(f'Checking admin {username}')
        if admin:
            if admin['password'] == password:
                return jsonify({'success': True, 'message': 'Login successful', 'role': 'admin'})

        print('Invalid credentials')
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except mysql.connector.Error as err:
        print(f'Database error: {err}')     
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500


@app.route('/doctors', methods=['GET'])
def get_doctors():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username FROM doctors")
        doctors = cursor.fetchall()
        return jsonify({'success': True, 'doctors': doctors})
    except mysql.connector.Error as e:
        print(f"Error fetching doctors: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500


@app.route('/admins', methods=['GET'])
def get_admins():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username FROM admins")
        admins = cursor.fetchall()
        return jsonify({'success': True, 'admins': admins})
    except mysql.connector.Error as e:
        print(f"Error fetching admins: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500


@app.route('/admins', methods=['POST'])
def add_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    try:
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO admins (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        db.commit()
        return jsonify({'success': True, 'message': 'Admin added successfully', 'admin_id': cursor.lastrowid})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({'success': False, 'message': f'Failed to add admin: {err}'}), 500


@app.route('/doctors', methods=['POST'])
def add_doctor():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO doctors (username, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        db.commit()
        return jsonify({'success': True, 'message': 'Doctor added successfully'}), 201
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({'success': False, 'message': f'Failed to add doctor: {err}'}), 500


@app.route('/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404
        return jsonify({'success': True, 'message': 'Admin deleted successfully'})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete admin: {err}'}), 500



@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    name = data.get('name')
    try:
        age = int(data.get('age'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '年龄必须是一个有效的数字'}), 400
    gender = data.get('gender')
    contact_info = data.get('contact_info')
    print(f'Add patient: {data}')
    
    if not all([name, age, gender, contact_info]):
        return jsonify({'success': False, 'message': '姓名、年龄、性别和联系方式均为必填项'}), 400

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO patients (name, age, gender, contact_info) VALUES (%s, %s, %s, %s)",
            (name, age, gender, contact_info)
        )
        db.commit()
        return jsonify({'success': True, 'message': '患者添加成功', 'patient_id': cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        print(f"DATABASE ERROR in add_patient: {err}")  # Explicitly log the error
        db.rollback()
        return jsonify({'success': False, 'message': f'数据库错误: {err}'}), 500



@app.route('/patients', methods=['GET'])
def get_patients():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, age, gender, contact_info, created_at FROM patients")
        patients = cursor.fetchall()
        return jsonify({'success': True, 'patients': patients})
    except mysql.connector.Error as e:
        print(f"Error fetching patients: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500


@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        return jsonify({'success': True, 'message': 'Patient deleted successfully'})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete patient: {err}'}), 500



@app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Doctor not found'}), 404
        return jsonify({'success': True, 'message': 'Doctor deleted successfully'})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete doctor: {err}'}), 500


@app.route('/patients/<int:patient_id>/diagnoses', methods=['POST'])
def create_diagnosis(patient_id):
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        unique_filename = f'{uuid.uuid4()}-{filename}'
        
        try:
            # Upload to MinIO
            s3_client.upload_fileobj(
                file,
                MINIO_BUCKET_NAME,
                unique_filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            file_url = f'http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{unique_filename}'

            # Save to database
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO diagnoses (patient_id, notes) VALUES (%s, %s)",
                (patient_id, 'New diagnosis with image upload.')
            )
            diagnosis_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO case_images (diagnosis_id, image_url) VALUES (%s, %s)",
                (diagnosis_id, file_url)
            )
            db.commit()
            cursor.close()
            db.close()

            return jsonify({
                'success': True, 
                'message': f'Successfully created diagnosis {diagnosis_id} and uploaded image.'
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'An error occurred: {e}'}), 500

    return jsonify({'success': False, 'message': 'An unknown error occurred'}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    from datetime import datetime, timedelta
    import random
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Doctors count per day
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(id) as count
            FROM doctors
            GROUP BY DATE(created_at)
            ORDER BY date;
        """)
        doctors_stats = cursor.fetchall()

        # Patients count per day
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(id) as count
            FROM patients
            GROUP BY DATE(created_at)
            ORDER BY date;
        """)
        patients_stats = cursor.fetchall()

        # Diagnoses count per day
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(id) as count
            FROM diagnoses
            GROUP BY DATE(created_at)
            ORDER BY date;
        """)
        diagnoses_stats = cursor.fetchall()

        # 如果数据库中没有数据，生成模拟数据用于演示
        if not doctors_stats and not patients_stats and not diagnoses_stats:
            # 生成过去30天的模拟数据
            base_date = datetime.now() - timedelta(days=30)
            
            doctors_stats = []
            patients_stats = []
            diagnoses_stats = []
            
            for i in range(30):
                current_date = base_date + timedelta(days=i)
                date_str = current_date.strftime('%Y-%m-%d')
                
                # 模拟医生注册数据（逐渐增长）
                doctor_count = random.randint(1, 5) if i < 20 else random.randint(0, 2)
                if doctor_count > 0:
                    doctors_stats.append({
                        'date': date_str,
                        'count': doctor_count
                    })
                
                # 模拟患者数据（波动增长）
                patient_count = random.randint(5, 25) + int(i * 0.5)
                patients_stats.append({
                    'date': date_str,
                    'count': patient_count
                })
                
                # 模拟诊断数据（基于患者数量）
                diagnosis_count = random.randint(3, int(patient_count * 0.8))
                diagnoses_stats.append({
                    'date': date_str,
                    'count': diagnosis_count
                })

        return jsonify({
            'success': True,
            'doctors': doctors_stats,
            'patients': patients_stats,
            'diagnoses': diagnoses_stats
        })

    except mysql.connector.Error as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500



ALLOWED_EXTENSIONS = {'dcm', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that delegates to SymptomExtractor.chat_top."""
    log_user_interaction(action="聊天请求", details=f"IP: {request.remote_addr}, Content-Type: {request.content_type}")
    
    content_type = request.content_type or ''
    extractor = get_symptom_extractor()  # 使用全局实例
    
    # Debug logging
    app.logger.info(f'Content-Type: {content_type}')
    app.logger.info(f'Form data keys: {list(request.form.keys())}')
    app.logger.info(f'Files keys: {list(request.files.keys())}')

    try:
        if content_type.startswith('multipart/form-data'):
            files = request.files.getlist('file')
            prompt = (request.form.get('prompt') or '').strip()
            
            app.logger.info(f'Prompt received: "{prompt}"')
            app.logger.info(f'Number of files: {len(files)}')
            
            if not prompt:
                app.logger.error('Prompt is empty or missing')
                return jsonify({'success': False, 'message': 'Prompt is required'}), 400

            if not files or all(f.filename == '' for f in files):
                app.logger.error('No valid files found')
                return jsonify({'success': False, 'message': 'No files selected'}), 400

            for file in files:
                app.logger.info(f'Processing file: {file.filename if file else "None"}')
                if file and file.filename:
                    app.logger.info(f'File extension check for: {file.filename}')
                    if allowed_file(file.filename):
                        app.logger.info(f'File {file.filename} is allowed, processing...')
                        image_bytes = file.read()
                        app.logger.info(f'Read {len(image_bytes)} bytes from file')
                        reply = extractor.chat_top(prompt, image_bytes)
                        app.logger.info('Successfully processed image')
                        return jsonify({'success': True, 'reply': reply})
                    else:
                        app.logger.warning(f'File {file.filename} not allowed')
                else:
                    app.logger.warning(f'Invalid file object or empty filename')

            app.logger.error('No valid image files found after processing all files')
            return jsonify({'success': False, 'message': 'No valid image files provided'}), 400
        elif content_type.startswith('application/json'):
            data = request.get_json(silent=True) or {}
            prompt = (data.get('message') or '').strip()
            if not prompt:
                return jsonify({'success': False, 'message': 'No message provided'}), 400
            # 无图文本对话
            reply = extractor.chat_with_gpt(prompt, '')
            return jsonify({'success': True, 'reply': reply})
        else:
            return jsonify({'success': False, 'message': 'Unsupported Content-Type'}), 415

    except Exception as e:
        app.logger.error(f'An error occurred in /chat: {e}')
        log_error(f"Chat路由异常: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Internal error: {e}'}), 500


@app.route('/generate-case', methods=['POST'])
def generate_case():
    """生成病例报告的API端点，支持文本数据和图片附件"""
    app.logger.info("📄 收到病例生成请求")
    
    try:
        # 检查是否有文件上传
        has_files = len(request.files) > 0
        app.logger.info(f"是否包含文件: {has_files}")
        
        # 处理文本数据
        if has_files:
            # 如果有文件上传，从 form 中获取数据
            data = {
                'name': request.form.get('name', ''),
                'age': request.form.get('age', ''),
                'gender': request.form.get('gender', ''),
                'medicalRecordNumber': request.form.get('medicalRecordNumber', ''),
                'visitDate': request.form.get('visitDate', ''),
                'reportDate': request.form.get('reportDate', ''),
                'reportingPhysician': request.form.get('reportingPhysician', ''),
                'chiefComplaint': request.form.get('chiefComplaint', ''),
                'presentIllness': request.form.get('presentIllness', ''),
                'pastHistory': request.form.get('pastHistory', ''),
                'physicalExam': request.form.get('physicalExam', '')
            }
        else:
            # 没有文件上传，从 JSON 中获取数据
            data = request.get_json()
            
        app.logger.info(f"请求数据: {data}")
        
        # 验证必填字段
        if not data or not data.get('chiefComplaint'):
            app.logger.warning("主诉为空，返回400错误")
            return jsonify({
                'success': False,
                'message': '主诉不能为空'
            }), 400
        
        # 提取患者信息
        name = data.get('name', '')
        age = data.get('age', '')
        gender = data.get('gender', '')
        medical_record_number = data.get('medicalRecordNumber', '')
        visit_date = data.get('visitDate', '')
        report_date = data.get('reportDate', '')
        reporting_physician = data.get('reportingPhysician', '')
        chief_complaint = data.get('chiefComplaint', '')
        present_illness = data.get('presentIllness', '')
        past_history = data.get('pastHistory', '')
        physical_exam = data.get('physicalExam', '')
        
        app.logger.info(f"患者信息 - 年龄: '{age}', 性别: '{gender}'")
        app.logger.info(f"主诉: '{chief_complaint}'")
        app.logger.info(f"现病史: '{present_illness}'")
        app.logger.info(f"既往史: '{past_history}'")
        app.logger.info(f"体格检查: '{physical_exam}'")
        
        # 处理图片附件
        image_attachments = []
        if has_files:
            app.logger.info("📎 开始处理图片附件...")
            # datetime已在文件顶部导入
            
            for file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    # 检查文件类型
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if file_ext in allowed_extensions:
                        # 读取文件内容
                        file_content = file.read()
                        file_size = len(file_content)
                        
                        # 将图片转换为base64格式，直接嵌入到病例报告中
                        # base64已在文件顶部导入
                        base64_data = base64.b64encode(file_content).decode('utf-8')
                        data_url = f"data:image/{file_ext};base64,{base64_data}"
                        
                        attachment_info = {
                            'filename': file.filename,
                            'size': file_size,
                            'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'data_url': data_url,  # 使用base64数据而不是SM.MS链接
                            'file_type': file_ext
                        }
                        
                        image_attachments.append(attachment_info)
                        app.logger.info(f"✅ 处理图片: {file.filename} ({file_size} bytes)")
                    else:
                        app.logger.warning(f"不支持的文件类型: {file.filename}")
            
            app.logger.info(f"📎 共处理 {len(image_attachments)} 个有效图片附件")
        
        # 使用SymptomExtractor生成病例
        app.logger.info("🤖 创建SymptomExtractor实例...")
        extractor = get_symptom_extractor()  # 使用全局实例
        
        app.logger.info("📝 开始生成病例报告...")
        case_report = extractor.generate_case_report({
            'name': name,
            'age': age,
            'gender': gender,
            'medicalRecordNumber': medical_record_number,
            'visitDate': visit_date,
            'reportDate': report_date,
            'reportingPhysician': reporting_physician,
            'chiefComplaint': chief_complaint,
            'presentIllness': present_illness,
            'pastHistory': past_history,
            'physicalExam': physical_exam
        }, image_attachments)
        
        app.logger.info(f"✅ 病例报告生成成功，长度: {len(case_report)} 字符")
        
        return jsonify({
            'success': True,
            'caseReport': case_report
        })
        
    except Exception as e:
        app.logger.error(f"❌ 生成病例错误: {str(e)}")
        # traceback已在文件顶部导入
        app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'生成病例失败: {str(e)}'
        }), 500


@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """将病例报告导出为PDF文件"""
    app.logger.info("📄 收到PDF导出请求")
    
    try:
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400
        
        content = data.get('content', '')
        filename = data.get('filename', 'case_report')
        
        # PDF生成所需的库已在文件顶部导入
        
        # 创建内存中的PDF文件
        buffer = io.BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 获取样式
        styles = getSampleStyleSheet()
        
        # 尝试注册中文字体（如果系统中有的话）
        try:
            # 支持中文的字体路径（优先使用中文字体）
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # WQY中文字体
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Noto CJK字体
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/System/Library/Fonts/Arial.ttf',  # macOS
                'C:/Windows/Fonts/simhei.ttf',  # Windows中文字体
            ]
            
            font_registered = False
            for font_path in font_paths:
                try:
                    # os已在文件顶部导入
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        font_registered = True
                        break
                except:
                    continue
            
            font_name = 'ChineseFont' if font_registered else 'Helvetica'
        except:
            font_name = 'Helvetica'
        
        # 创建自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            spaceAfter=30,
            alignment=1  # 居中
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            spaceAfter=6,
            leftIndent=0
        )
        
        # 辅助函数：处理base64图片
        def process_base64_image(data_url):
            try:
                # 解析data URL
                if not data_url.startswith('data:'):
                    return None
                
                # 提取base64数据
                header, data = data_url.split(',', 1)
                image_data = base64.b64decode(data)
                
                # 使用PIL处理图片
                pil_image = PILImage.open(io.BytesIO(image_data))
                
                # 调整图片大小以适应PDF页面
                max_width = 400  # 最大宽度
                max_height = 300  # 最大高度
                
                # 计算缩放比例
                width_ratio = max_width / pil_image.width
                height_ratio = max_height / pil_image.height
                scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大图片
                
                new_width = int(pil_image.width * scale_ratio)
                new_height = int(pil_image.height * scale_ratio)
                
                # 调整图片大小
                if scale_ratio < 1.0:
                    pil_image = pil_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                
                # 转换为RGB模式（PDF需要）
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # 保存到内存
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='JPEG', quality=85)
                img_buffer.seek(0)
                
                # 创建ReportLab Image对象
                return Image(img_buffer, width=new_width, height=new_height)
                
            except Exception as e:
                app.logger.error(f"处理图片失败: {str(e)}")
                return None
        
        # 构建文档内容
        story = []
        
        # 将内容按行处理
        lines = content.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # 检查是否包含base64图片
            img_match = re.search(r'<img\s+src="(data:[^"]+)"[^>]*>', line)
            if img_match:
                data_url = img_match.group(1)
                img_obj = process_base64_image(data_url)
                if img_obj:
                    story.append(Spacer(1, 12))  # 图片前的间距
                    story.append(img_obj)
                    story.append(Spacer(1, 12))  # 图片后的间距
                else:
                    # 如果图片处理失败，显示提示文本
                    story.append(Paragraph("[图片显示失败]", normal_style))
                i += 1
                continue
            
            # 检查是否是标题（以#开头或包含数字编号）
            if line.startswith('#'):
                # 去掉#符号
                title_text = re.sub(r'^#+\s*', '', line)
                if '病例报告' in title_text:
                    story.append(Paragraph(title_text, title_style))
                else:
                    story.append(Paragraph(title_text, heading_style))
            elif re.match(r'^\d+\.\s+', line):  # 数字编号的标题
                story.append(Paragraph(line, heading_style))
            elif line.startswith('**') and line.endswith('**'):  # 粗体标题
                title_text = line.replace('**', '')
                story.append(Paragraph(title_text, heading_style))
            else:
                # 处理普通文本，转义HTML特殊字符（但保留图片标签）
                if '<img' not in line:
                    escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # 处理粗体标记
                    escaped_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped_line)
                    story.append(Paragraph(escaped_line, normal_style))
                else:
                    # 如果包含图片标签但没有匹配到，跳过这行
                    pass
            
            i += 1
        
        # 生成PDF
        doc.build(story)
        
        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()
        
        app.logger.info(f"✅ PDF生成成功，大小: {len(pdf_data)} bytes")
        
        # 返回PDF文件
        # Response和urllib.parse已在文件顶部导入
        
        # 处理中文文件名编码问题
        encoded_filename = urllib.parse.quote(f'{filename}.pdf')
        
        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename*=UTF-8\'\'{encoded_filename}',
                'Content-Length': str(len(pdf_data))
            }
        )
        
        return response
        
    except Exception as e:
        app.logger.error(f"PDF导出失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'PDF导出失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    # 记录系统启动
    log_system_startup()
    
    # 初始化RAG系统
    print("🚀 正在初始化医学RAG系统...")
    log_info("开始初始化医学RAG系统")
    try:
        # initialize_medical_rag已在文件顶部导入
        initialize_medical_rag()
        print("✅ 医学RAG系统初始化完成")
        log_info("医学RAG系统初始化完成")
    except Exception as e:
        print(f"⚠️ RAG系统初始化失败: {e}")
        print("系统将继续运行，但诊断建议功能可能受影响")
        log_error(f"RAG系统初始化失败: {e}", exc_info=True)
    
    print("🏥 医疗AI聊天系统启动中...")
    log_info("医疗AI聊天系统启动，监听端口3000")
    app.run(debug=True, host='0.0.0.0', port=3000)
