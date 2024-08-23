from flask import Flask, render_template, request, jsonify
from main import VoiceAssistant
import threading
import os
import json

app = Flask(__name__)

assistant = None
assistant_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_assistant():
    global assistant, assistant_thread
    if assistant_thread is None or not assistant_thread.is_alive():
        assistant = VoiceAssistant()
        assistant_thread = threading.Thread(target=assistant.run)
        assistant_thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@app.route('/stop', methods=['POST'])
def stop_assistant():
    global assistant, assistant_thread
    if assistant_thread and assistant_thread.is_alive():
        assistant.stop()
        assistant_thread.join()
        assistant_thread = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})

@app.route('/restart', methods=['POST'])
def restart_assistant():
    stop_assistant()
    return start_assistant()

@app.route('/update_env', methods=['POST'])
def update_env():
    env_vars = request.json
    with open('.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    return jsonify({"status": "updated"})

@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    new_prompt = request.json['prompt']
    with open('prompt.py', 'w') as f:
        f.write(f"system_prompt = '''{new_prompt}'''")
    return jsonify({"status": "updated"})

@app.route('/toggle_tool', methods=['POST'])
def toggle_tool():
    tool_name = request.json['tool_name']
    enabled = request.json['enabled']
    # Implement logic to enable/disable tool in tools.py
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)