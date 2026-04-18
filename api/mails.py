from flask import Flask, request, jsonify
import json
import os
import time

app = Flask(__name__)

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

@app.route('/delete', methods=['GET'])
def delete_email():
    """حذف بريد مؤقت"""
    
    email = request.args.get('email')
    password = request.args.get('password')
    
    if not email or not password:
        return jsonify({
            "error": "Email and password required",
            "success": False
        }), 400
    
    data = load_data()
    
    if email not in data:
        return jsonify({
            "error": "Email not found",
            "success": False
        }), 404
    
    if data[email]["password"] != password:
        return jsonify({
            "error": "Invalid password",
            "success": False
        }), 401
    
    # حذف البريد
    del data[email]
    save_data(data)
    
    return jsonify({
        "success": True,
        "message": "Email deleted successfully"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)