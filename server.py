import os
import socket
import argparse
import time
import webbrowser
import shutil
import netifaces
import qrcode
import subprocess
import logging
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
# Default upload folder (can be overridden via CLI)
DEFAULT_UPLOAD_FOLDER = os.path.expanduser('~/Downloads')
app.config['UPLOAD_FOLDER'] = DEFAULT_UPLOAD_FOLDER
# 16GB limit, effectively unlimited for local transfer
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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

def find_open_port(host='0.0.0.0', start_port=5000, end_port=5099):
    """Find an available TCP port by trying to bind."""
    bind_host = host if host not in ('', '0.0.0.0') else '0.0.0.0'
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((bind_host, port))
                return port
            except OSError:
                continue
    return start_port

def build_url(ip, port, use_https):
    scheme = 'https' if use_https else 'http'
    return f"{scheme}://{ip}:{port}"

def copy_to_clipboard(text):
    """Best-effort clipboard copy on macOS."""
    try:
        if shutil.which('pbcopy'):
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
            return True
    except Exception:
        pass
    return False

# Global notification callback
notification_callback = None

def set_notification_callback(callback):
    global notification_callback
    notification_callback = callback

def send_notification(filename):
    """Sends a notification using the registered callback or fallback."""
    logger.info(f"Sending notification for: {filename}")
    try:
        # Play a sound immediately
        subprocess.Popen(['afplay', '/System/Library/Sounds/Glass.aiff'])
        
        if notification_callback:
            notification_callback("File Received", filename)
        else:
            # Fallback for when running standalone server without GUI wrapper
            logger.info("No notification callback registered (running in headless/server mode)")
            
    except Exception as e:
        logger.error(f"Notification error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/healthz')
def healthz():
    return {'status': 'ok'}, 200

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
            filename = f"shared_text_{int(time.time())}.txt"
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
    parser = argparse.ArgumentParser(description="AirTransfer file receiver (Flask).")
    parser.add_argument('--host', default='0.0.0.0', help="Host to bind (default: 0.0.0.0)")
    parser.add_argument('--port', type=int, default=0, help="Port to bind (default: auto 5000-5099)")
    parser.add_argument('--ip', default='', help="IP/hostname to advertise in the QR code (default: auto-detect)")
    parser.add_argument('--downloads', default=DEFAULT_UPLOAD_FOLDER, help="Destination folder (default: ~/Downloads)")

    tls = parser.add_mutually_exclusive_group()
    tls.add_argument('--https', action='store_true', help="Serve over HTTPS (self-signed) for PWA/share-target")
    tls.add_argument('--http', action='store_true', help="Serve over HTTP (useful for localhost testing)")
    parser.add_argument('--cert', default='', help="Path to TLS certificate PEM (enables HTTPS)")
    parser.add_argument('--key', default='', help="Path to TLS private key PEM (enables HTTPS)")

    parser.add_argument('--no-qr', action='store_true', help="Don't print ASCII QR code in terminal")
    parser.add_argument('--open', action='store_true', help="Open the URL in a browser")

    clip = parser.add_mutually_exclusive_group()
    clip.add_argument('--copy', dest='copy', action='store_true', help="Copy URL to clipboard (macOS pbcopy)")
    clip.add_argument('--no-copy', dest='copy', action='store_false', help="Don't copy URL to clipboard")
    parser.set_defaults(copy=True)

    args = parser.parse_args()

    # Configure upload folder
    upload_folder = os.path.expanduser(args.downloads)
    app.config['UPLOAD_FOLDER'] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

    local_ip = args.ip.strip() or get_ip_address()
    port = args.port if args.port else find_open_port(host=args.host, start_port=5000, end_port=5099)

    # If a cert/key is provided, we must use HTTPS.
    has_custom_tls = bool(args.cert.strip() or args.key.strip())
    if has_custom_tls and not (args.cert.strip() and args.key.strip()):
        raise SystemExit("Error: if you set --cert you must also set --key (and vice versa).")

    # Default to HTTPS because Android PWA/share-target requires a secure context.
    use_https = True
    if args.http:
        use_https = False
    elif args.https or has_custom_tls:
        use_https = True

    url = build_url(local_ip, port, use_https=use_https)

    if use_https and not has_custom_tls:
        print(
            "\nNOTE: You're using a self-signed HTTPS certificate.\n"
            "Chrome/Android will show 'Your connection is not private' (NET::ERR_CERT_AUTHORITY_INVALID).\n"
            "- Quick fix: tap Advanced → Proceed (unsafe)\n"
            "- If there's no Proceed button: tap anywhere on the page and type thisisunsafe\n"
            "- No-warning option: run with a trusted cert via --cert/--key (see README: mkcert setup)\n"
            "- Plain HTTP (no warning, but weaker/PWA features may be limited): run with --http\n"
        )
    else:
        print(f"\n✅ Running in Simple Mode (HTTP). No warnings.\nURL: {url}")

    if not args.no_qr:
        print_qr(url)

    if args.copy and copy_to_clipboard(url):
        print("URL copied to clipboard!")

    if args.open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    if use_https:
        ssl_context = (args.cert, args.key) if has_custom_tls else 'adhoc'
    else:
        ssl_context = None
    # Host 0.0.0.0 is required to be accessible from other devices
    app.run(host=args.host, port=port, debug=False, use_reloader=False, ssl_context=ssl_context)
