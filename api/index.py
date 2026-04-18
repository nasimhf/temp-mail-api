from flask import Flask, request, jsonify
import random
import string
import json
import os
import time
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "/tmp/temp_emails.json"

# قائمة نطاقات مقبولة من فيسبوك
ALLOWED_DOMAINS = [
    "@gmail.com",
    "@yahoo.com",
    "@outlook.com", 
    "@hotmail.com",
    "@protonmail.com",
    "@mail.com",
    "@icloud.com",
    "@aol.com",
    "@live.com"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    return jsonify({"status": "working", "message": "Temp Mail API is running"})

@app.route('/test')
def test():
    return jsonify({"status": "working"})

@app.route('/create', methods=['GET'])
def create_email():
    password = request.args.get('password', '')
    if not password:
        password = ''.join(random.choices(string.digits, k=8))
    
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
    # استخدام نطاق عشوائي مقبول من فيسبوك
    domain = random.choice(ALLOWED_DOMAINS)
    email = f"{username}{domain}"
    
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

@app.route('/mails', methods=['GET'])
def get_mails():
    email = request.args.get('email')
    password = request.args.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    data = load_data()
    
    if email not in data:
        return jsonify({"error": "Email not found"}), 404
    
    if data[email]["password"] != password:
        return jsonify({"error": "Invalid password"}), 401
    
    return jsonify({
        "success": True,
        "email": email,
        "messages": data[email].get("messages", []),
        "count": len(data[email].get("messages", []))
    })

@app.route('/delete', methods=['GET'])
def delete_email():
    email = request.args.get('email')
    password = request.args.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    data = load_data()
    
    if email not in data:
        return jsonify({"error": "Email not found"}), 404
    
    if data[email]["password"] != password:
        return jsonify({"error": "Invalid password"}), 401
    
    del data[email]
    save_data(data)
    
    return jsonify({"success": True, "message": "Email deleted"})

@app.route('/add_message', methods=['POST'])
def add_message():
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
    
    all_data[email]["messages"].append({
        "id": len(all_data[email]["messages"]) + 1,
        "subject": subject,
        "body": body,
        "from": sender,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(all_data)
    
    return jsonify({"success": True, "message": "تم إضافة الرسالة"})

@app.route('/list', methods=['GET'])
def list_emails():
    data = load_data()
    emails = []
    for email, info in data.items():
        emails.append({
            "email": email,
            "created_at": info.get("created_at_str"),
            "messages_count": len(info.get("messages", []))
        })
    return jsonify({"success": True, "count": len(emails), "emails": emails})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
