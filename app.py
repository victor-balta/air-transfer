import rumps
import threading
import server
import os
import qrcode

# Configuration
ICON_PATH = os.path.join(os.path.dirname(__file__), 'static', 'icon-192.png')
DEFAULT_CERT = os.path.join(os.path.dirname(__file__), 'certs', 'airtransfer-cert.pem')
DEFAULT_KEY = os.path.join(os.path.dirname(__file__), 'certs', 'airtransfer-key.pem')

class AirTransferApp(rumps.App):
    def __init__(self):
        # Set Menu Bar Icon (Template)
        menu_icon = os.path.join(os.path.dirname(__file__), "static/menubarTemplate.png")
        if not os.path.exists(menu_icon):
            menu_icon = ICON_PATH if os.path.exists(ICON_PATH) else None
        
        super(AirTransferApp, self).__init__("AirTransfer", icon=menu_icon, template=True)
        
        if not menu_icon:
            self.title = "📡"

        self.server_thread = None
        self.url = None
        
        self.menu = [
            "Show QR Code",
            "Copy URL",
            rumps.separator,
            "Open Downloads",
            "Test Notification",
            rumps.separator,
        ]
        
        # Start server automatically
        self.start_server()

    def send_notification(self, title, message):
        """Send notification using rumps (proven to work)."""
        rumps.notification("AirTransfer", title, message, sound=True)
        print(f"Notification sent: {title} - {message}")

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            return
            
        # Register notification callback
        server.set_notification_callback(self.send_notification)

        self.ip = server.get_ip_address()

        # Find available port and build URL
        use_http = os.environ.get('AIRTRANSFER_USE_HTTP', '').lower() in ('true', '1', 'yes')
        use_https = not use_http
        
        self.port = server.find_open_port(host='0.0.0.0', start_port=5000, end_port=5099)
        self.url = server.build_url(self.ip, self.port, use_https=use_https)

        # Prefer a trusted cert if provided
        cert = os.environ.get('AIRTRANSFER_CERT') or (DEFAULT_CERT if os.path.exists(DEFAULT_CERT) else '')
        key = os.environ.get('AIRTRANSFER_KEY') or (DEFAULT_KEY if os.path.exists(DEFAULT_KEY) else '')
        
        if use_https:
            ssl_context = (cert, key) if (cert and key) else 'adhoc'
        else:
            ssl_context = None
        
        # Auto-copy URL to clipboard
        server.copy_to_clipboard(self.url)
        
        # Run Flask
        self.server_thread = threading.Thread(
            target=lambda: server.app.run(
                host='0.0.0.0', 
                port=self.port, 
                debug=False, 
                use_reloader=False,
                ssl_context=ssl_context
            )
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"Server started at {self.url}")
        print("URL copied to clipboard!")

    @rumps.clicked("Copy URL")
    def copy_url(self, sender):
        if self.url:
            server.copy_to_clipboard(self.url)
            self.send_notification("URL Copied", self.url)

    @rumps.clicked("Show QR Code")
    def show_qr(self, sender):
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_path = "/tmp/airtransfer_qr.png"
        img.save(temp_path)
        os.system(f"open {temp_path}")

    @rumps.clicked("Open Downloads")
    def open_downloads(self, sender):
        os.system("open ~/Downloads")
        
    @rumps.clicked("Test Notification")
    def test_notification(self, sender):
        self.send_notification("Test", "This is a test notification!")

if __name__ == "__main__":
    AirTransferApp().run()
