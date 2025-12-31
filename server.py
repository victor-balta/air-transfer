import os
import socket
import netifaces
import qrcode
import subprocess
import logging
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = os.path.expanduser('~/Downloads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 16GB limit, effectively unlimited for local transfer
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_ip_address():
    # Try getting the local IP address
    try:
        # Check standard interfaces
        for interface in netifaces.interfaces():
            if interface == 'lo': continue
            if_addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in if_addrs:
                for addr in if_addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Prefer standard private ranges
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        return ip
    except Exception:
        pass
    
    # Fallback method: try to connect to an external server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def send_notification(filename):
    """Sends a native macOS notification using terminal-notifier."""
    logger.info(f"Sending notification for: {filename}")
    try:
        # Play a sound immediately
        subprocess.Popen(['afplay', '/System/Library/Sounds/Glass.aiff'])
        
        # Send notification via terminal-notifier
        subprocess.run([
            'terminal-notifier',
            '-title', 'AirTransfer',
            '-subtitle', 'File Received',
            '-message', filename,
            '-sound', 'default'
        ])
    except Exception as e:
        logger.error(f"Notification error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
        
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return {'error': 'No selected file'}, 400
        
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Handle duplicate filenames by appending a number
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(destination):
            destination = os.path.join(app.config['UPLOAD_FOLDER'], f"{base}_{counter}{ext}")
            counter += 1
            
        try:
            file.save(destination)
            saved_files.append(os.path.basename(destination))
            send_notification(os.path.basename(destination))
        except Exception as e:
            return {'error': str(e)}, 500
        
    return {'status': 'success', 'files': saved_files}, 200

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
            filename = f"shared_text_{int(__import__('time').time())}.txt"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'w') as f:
                f.write(shared_text)
            send_notification(filename)
            logger.info(f"Saved shared text to {filename}")
            return redirect('/')
    return redirect('/')

def print_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    print("\n" + "="*40)
    print(f"Scan this QR code to upload files:\n{url}")
    print("="*40 + "\n")
    # Invert colors for better visibility in dark terminals, or standard
    qr.print_ascii(invert=True)
    print("\n" + "="*40 + "\n")

if __name__ == '__main__':
    local_ip = get_ip_address()
    
    # helper to find an open port
    def find_open_port(start_port=5000):
        # Scan a range of ports
        for port in range(start_port, start_port + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    continue
        return start_port
        
    port = find_open_port()
    url = f"http://{local_ip}:{port}"
    print_qr(url)
    # Host 0.0.0.0 is required to be accessible from other devices
    app.run(host='0.0.0.0', port=port)
