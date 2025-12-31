import os
import socket
import subprocess
import logging
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = os.path.expanduser('~/Downloads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads dir if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_ip_address():
    """Finds the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        s.close()
    except Exception:
        IP = '127.0.0.1'
    return IP

def send_notification(filename):
    """Sends a native macOS notification using terminal-notifier."""
    logger.info(f"Sending notification for: {filename}")
    try:
        # Play a sound immediately
        subprocess.Popen(['afplay', '/System/Library/Sounds/Glass.aiff'])
        
        # Build command
        cmd = [
            'terminal-notifier',
            '-title', 'AirTransfer',
            '-subtitle', 'File Received',
            '-message', filename,
            '-sound', 'default'
        ]
        
        # Add app icon if it exists
        icon_path = os.path.join(app.root_path, 'static', 'app_icon.png')
        if os.path.exists(icon_path):
            cmd.extend(['-appIcon', icon_path])
            
        subprocess.run(cmd)
    except Exception as e:
        logger.error(f"Notification error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Handle duplicate filenames
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base}_{counter}{ext}")
            counter += 1
            
        try:
            file.save(filepath)
            logger.info(f"File saved to {filepath}")
            send_notification(os.path.basename(filepath))
            return 'File uploaded successfully', 200
        except Exception as e:
            logger.error(f"Save error: {e}")
            return f"Save failed: {str(e)}", 500

@app.route('/share', methods=['GET', 'POST'])
def share_target():
    """Handle Android Share Target API requests."""
    if request.method == 'POST':
        # Handle shared files
        if 'file' in request.files:
            return upload_file()
        # Handle shared text/URL
        shared_text = request.form.get('text') or request.form.get('url')
        if shared_text:
            # Save shared text to a file
            filename = f"shared_text_{int(time.time())}.txt"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'w') as f:
                f.write(shared_text)
            send_notification(filename)
            logger.info(f"Saved shared text to {filename}")
            return redirect('/')
    return redirect('/')

if __name__ == '__main__':
    ip = get_ip_address()
    print(f"Server running at http://{ip}:5000")
    app.run(host='0.0.0.0', port=5000)
