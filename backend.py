from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    print("New Feedback Received:")
    print(f"Name: {data.get('name')}")
    print(f"Email: {data.get('email')}")
    print(f"Issue: {data.get('issue')}")
    print(f"Message: {data.get('message')}")
    return jsonify({'success': True, 'message': 'Feedback received'})

if __name__ == '__main__':
    print("🚀 K Tube Tools Backend Running")
    app.run(host='0.0.0.0', port=5000, debug=True)
