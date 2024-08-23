import subprocess
import os
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Global variable to store the subprocess
main_process = None

# Path to the virtual environment
venv_path = os.path.join(os.getcwd(), 'venv')
venv_activate = os.path.join(venv_path, 'bin', 'activate')

def run_in_venv(command):
    return f'source {venv_activate} && {command}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_config', methods=['GET'])
def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return jsonify(config)

@app.route('/update_config', methods=['POST'])
def update_config():
    new_config = request.json
    with open('config.json', 'w') as f:
        json.dump(new_config, f, indent=2)
    return jsonify({"status": "success"})

@app.route('/get_prompt', methods=['GET'])
def get_prompt():
    with open('prompt.py', 'r') as f:
        prompt = f.read()
    return jsonify({"prompt": prompt})

@app.route('/update_prompt', methods=['POST'])
def update_prompt():
    new_prompt = request.json['prompt']
    with open('prompt.py', 'w') as f:
        f.write(new_prompt)
    return jsonify({"status": "success"})

@socketio.on('start_main')
def start_main():
    global main_process
    if main_process is None or main_process.poll() is not None:
        cmd = run_in_venv('python main.py')
        main_process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        return {"status": "started"}
    return {"status": "already_running"}

@socketio.on('stop_main')
def stop_main():
    global main_process
    if main_process and main_process.poll() is None:
        main_process.terminate()
        main_process = None
        return {"status": "stopped"}
    return {"status": "not_running"}

@socketio.on('restart_main')
def restart_main():
    stop_main()
    return start_main()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)