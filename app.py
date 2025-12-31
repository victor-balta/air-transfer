import rumps
import threading
import server
import webbrowser
import os
import qrcode
import subprocess
from PIL import Image

# Configuration
ICON_PATH = os.path.join(os.path.dirname(__file__), 'static', 'menubar_icon_v2.png')

class AirTransferApp(rumps.App):
    def __init__(self):
        # Try to use custom icon, fallback to emoji
        icon = ICON_PATH if os.path.exists(ICON_PATH) else None
        super(AirTransferApp, self).__init__("AirTransfer", icon=icon)
        if not icon:
            self.title = "📡"
            
        self.template = True # Ensure macOS treats it as a template icon (dark/light mode)
        self.server_thread = None
        self.url = None
        
        self.menu = [
            "Show QR Code",
            "Copy URL",
            rumps.separator,
            "Open Downloads",
            rumps.separator,
        ]
        
        # Start server automatically
        self.start_server()

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            return

        self.ip = server.get_ip_address()
        
        # Find available port (Start at 5002 to avoid conflicts)
        import socket
        def find_port():
            for p in range(5002, 5100):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('0.0.0.0', p))
                        return p
                    except:
                        continue
            return 5002
            
        self.port = find_port()
        self.url = f"http://{self.ip}:{self.port}"
        
        # Auto-copy URL to clipboard
        subprocess.run(['pbcopy'], input=self.url.encode(), check=True)
        
        # Run Flask
        self.server_thread = threading.Thread(
            target=lambda: server.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"Server started at {self.url}")
        print("URL copied to clipboard!")
        
        # Print QR code to terminal
        qr = qrcode.QRCode()
        qr.add_data(self.url)
        qr.make(fit=True)
        print("\nScan this QR code to connect:\n")
        qr.print_ascii(invert=True)
        print("\n")

    @rumps.clicked("Copy URL")
    def copy_url(self, sender):
        if self.url:
            subprocess.run(['pbcopy'], input=self.url.encode(), check=True)
            rumps.notification("AirTransfer", "URL Copied", self.url, sound=False)

    @rumps.clicked("Show QR Code")
    def show_qr(self, sender):
        # Generate QR image temporarily
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_path = "/tmp/airtransfer_qr.png"
        img.save(temp_path)
        
        # Preview it using 'open' (Preview.app)
        os.system(f"open {temp_path}")

    @rumps.clicked("Open Downloads")
    def open_downloads(self, sender):
        os.system("open ~/Downloads")

if __name__ == "__main__":
    AirTransferApp().run()
