from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "working",
        "message": "API is running successfully!"
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "success",
        "code": 200,
        "message": "Test endpoint is working"
    })

@app.route('/create')
def create():
    return jsonify({
        "success": True,
        "email": "test@tempmail.com",
        "password": "123456"
    })
