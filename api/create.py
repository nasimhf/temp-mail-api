from flask import Flask, request, jsonify
import random
import string
import json
import os
import time

app = Flask(__name__)

# ملف تخزين البيانات (في /tmp لأن Vercel يسمح بالكتابة هناك فقط)
DATA_FILE = "/tmp/emails.json"

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
            json.dump(data, f, indent=2)
        return True
    except:
        return False

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
    domain = "@tempmail.com"
    email = username + domain
    
    # حفظ البيانات
    data = load_data()
    data[email] = {
        "password": password,
        "messages": [],
        "created_at": time.time()
    }
    save_data(data)
    
    return jsonify({
        "success": True,
        "email": email,
        "password": password,
        "message": "تم إنشاء البريد بنجاح"
    })

@app.route('/test', methods=['GET'])
def test():
    """اختبار أن الـ API يعمل"""
    return jsonify({
        "status": "working",
        "message": "Temp Mail API is running",
        "endpoints": ["/create", "/mails", "/delete", "/test"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)