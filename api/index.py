from flask import Flask, request, jsonify
import random
import string
import json
import os
import time
from datetime import datetime

app = Flask(__name__)

# ملف تخزين البيانات
DATA_FILE = "/tmp/temp_emails.json"

def load_data():
    """تحميل البيانات من الملف"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    """حفظ البيانات في الملف"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# ==================== API إنشاء بريد مؤقت ====================
@app.route('/create', methods=['GET'])
def create_email():
    """إنشاء بريد مؤقت جديد"""
    
    # الحصول على كلمة المرور من الطلب
    password = request.args.get('password', '')
    
    # إذا لم تكن هناك كلمة مرور، أنشئ واحدة عشوائية
    if not password:
        password = ''.join(random.choices(string.digits, k=8))
    
    # إنشاء اسم مستخدم عشوائي
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@tempmail.com"
    
    # حفظ البيانات
    data = load_data()
    data[email] = {
        "password": password,
        "messages": [],
        "created_at": time.time(),
        "created_at_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_data(data)
    
    return jsonify({
        "success": True,
        "email": email,
        "password": password,
        "message": "تم إنشاء البريد بنجاح"
    })

# ==================== API جلب الرسائل ====================
@app.route('/mails', methods=['GET'])
def get_mails():
    """جلب قائمة الرسائل الواردة"""
    
    email = request.args.get('email')
    password = request.args.get('password')
    
    # التحقق من وجود البريد وكلمة المرور
    if not email or not password:
        return jsonify({
            "error": "Email and password required",
            "success": False
        }), 400
    
    # تحميل البيانات
    data = load_data()
    
    # التحقق من وجود البريد
    if email not in data:
        return jsonify({
            "error": "Email not found",
            "success": False
        }), 404
    
    # التحقق من صحة كلمة المرور
    if data[email]["password"] != password:
        return jsonify({
            "error": "Invalid password",
            "success": False
        }), 401
    
    # إرجاع الرسائل
    return jsonify({
        "success": True,
        "email": email,
        "messages": data[email].get("messages", []),
        "count": len(data[email].get("messages", []))
    })

# ==================== API إضافة رسالة (للاستخدام الداخلي) ====================
@app.route('/add_message', methods=['POST'])
def add_message():
    """إضافة رسالة جديدة (للاستخدام من تطبيقات أخرى)"""
    
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    subject = data.get('subject', 'بدون موضوع')
    body = data.get('body', '')
    sender = data.get('from', 'مرسل غير معروف')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    all_data = load_data()
    
    if email not in all_data:
        return jsonify({"error": "Email not found"}), 404
    
    if all_data[email]["password"] != password:
        return jsonify({"error": "Invalid password"}), 401
    
    # إضافة الرسالة
    all_data[email]["messages"].append({
        "id": len(all_data[email]["messages"]) + 1,
        "subject": subject,
        "body": body,
        "from": sender,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(all_data)
    
    return jsonify({
        "success": True,
        "message": "تم إضافة الرسالة بنجاح"
    })

# ==================== API حذف بريد ====================
@app.route('/delete', methods=['GET'])
def delete_email():
    """حذف بريد مؤقت"""
    
    email = request.args.get('email')
    password = request.args.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    data = load_data()
    
    if email not in data:
        return jsonify({"error": "Email not found"}), 404
    
    if data[email]["password"] != password:
        return jsonify({"error": "Invalid password"}), 401
    
    # حذف البريد
    del data[email]
    save_data(data)
    
    return jsonify({
        "success": True,
        "message": "Email deleted successfully"
    })

# ==================== API اختبار ====================
@app.route('/test', methods=['GET'])
def test():
    """اختبار أن الـ API يعمل"""
    return jsonify({
        "status": "working",
        "message": "Temp Mail API is running",
        "endpoints": [
            "/create?password=123456",
            "/mails?email=user@tempmail.com&password=123456",
            "/delete?email=user@tempmail.com&password=123456",
            "/add_message (POST)",
            "/test"
        ]
    })

# ==================== API قائمة جميع البريد ====================
@app.route('/list', methods=['GET'])
def list_emails():
    """عرض قائمة جميع البريد (للمطور فقط)"""
    
    data = load_data()
    emails = []
    
    for email, info in data.items():
        emails.append({
            "email": email,
            "created_at": info.get("created_at_str"),
            "messages_count": len(info.get("messages", []))
        })
    
    return jsonify({
        "success": True,
        "count": len(emails),
        "emails": emails
    })

@app.route('/')
def home():
    return jsonify({
        "status": "working",
        "message": "Temp Mail API is running",
        "developer": "@modedevx"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
