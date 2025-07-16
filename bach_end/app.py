import os
import uuid
import base64
import boto3
import mysql.connector
from openai import OpenAI
import json
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

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

        # Patients count per day (assuming a patients table exists)
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
    # Definitive fix: Temporarily remove all known proxy environment variables
    proxy_keys = ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
    original_proxies = {key: os.environ.get(key) for key in proxy_keys}

    for key in proxy_keys:
        if key in os.environ:
            del os.environ[key]

    try:
        # Initialize the client in a proxy-free environment
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    finally:
        # Restore all original proxy settings
        for key, value in original_proxies.items():
            if value is not None:
                os.environ[key] = value
    content_type = request.content_type

    try:
        messages = []
        # Handle multimodal (file + text) requests
        if content_type.startswith('multipart/form-data'):
            files = request.files.getlist('file')
            prompt = request.form.get('prompt', 'Describe the image(s).')
            if not prompt or not prompt.strip():
                prompt = 'Describe the image(s).'

            if not files or all(f.filename == '' for f in files):
                return jsonify({'success': False, 'message': 'No files selected'}), 400

            # OpenAI format for multimodal messages
            content_parts = [{'type': 'text', 'text': prompt}]
            image_added = False
            for file in files:
                if file and allowed_file(file.filename):
                    image_bytes = file.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = file.content_type
                    data_url = f"data:{mime_type};base64,{base64_image}"
                    content_parts.append({
                        'type': 'image_url',
                        'image_url': {
                            'url': data_url
                        }
                    })
                    image_added = True
            
            if not image_added:
                return jsonify({'success': False, 'message': 'No valid image files provided'}), 400

            messages.append({'role': 'user', 'content': content_parts})

        # Handle text-only requests
        elif content_type.startswith('application/json'):
            data = request.get_json()
            message = data.get('message')
            if not message:
                return jsonify({'success': False, 'message': 'No message provided'}), 400
            messages.append({'role': 'user', 'content': message})

        else:
            return jsonify({'success': False, 'message': 'Unsupported Content-Type'}), 415

        # Send request to DeepSeek API using OpenAI SDK
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        
        reply = response.choices[0].message.content
        return jsonify({'success': True, 'reply': reply})

    except Exception as e:
        app.logger.error(f"An error occurred in /chat: {e}")
        return jsonify({'success': False, 'message': f'An internal error occurred: {e}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
