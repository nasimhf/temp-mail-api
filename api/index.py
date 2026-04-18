from flask import Flask, request, jsonify
import random
import string
import json
import os
import time

app = Flask(__name__)
DATA_FILE = "/tmp/emails.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/create', methods=['GET'])
def create_email():
    password = request.args.get('password', '')
    if not password:
        password = ''.join(random.choices(string.digits, k=8))
    
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@tempmail.com"
    
    data = load_data()
    data[email] = {
        "password": password,
        "messages": [],
        "created_at": time.time()
    }
    save_data(data)
    
    return jsonify({"success": True, "email": email, "password": password})

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
        "messages": data[email].get("messages", []),
        "count": len(data[email].get("messages", []))
    })

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "working"})

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
