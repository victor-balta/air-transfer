# AirTransfer

**Transfer files from your Android phone to your Mac instantly over Wi-Fi.**

A lightweight, self-hosted alternative to AirDrop for Android ↔ Mac file transfers.

## Features

- 📱 **Simple Web UI** - Works on any device with a browser
- 🍎 **Native Mac App** - Menu bar icon, native notifications, and drag-and-drop support
- 🚀 **Fast** - Transfers at local Wi-Fi speeds
- 🔒 **Private** - Data never leaves your local network

## Quick Start

### 1. Run the App
```bash
./start.sh
```
This launches the Menu Bar app. A QR code will also appear in your terminal.

### 2. Connect
Scan the QR code with your phone. 
- By default, it runs in **HTTP Mode** (Simple Mode) so you can connect instantly without security warnings.
- Select files to upload, and they will appear in your Mac's `~/Downloads` folder.

## Advanced Usage

### HTTPS Mode (PWA Support)
If you want to install the app as a PWA or use the Android "Share Target" feature (sharing directly from other apps), you need HTTPS.

1. Generate a trusted local certificate:
   ```bash
   ./gen_certs.sh
   ```
   Follow the instructions to install the Root CA on your phone.

2. Run the app:
   ```bash
   ./start.sh
   ```
   (It automatically detects the certs in `certs/` and switches to HTTPS).

### Building the Native Mac App
To get the proper Dock icon and notifications, the app runs as a bundled macOS application. You can rebuild it if you change the code:

```bash
./build_app.sh
```

## Troubleshooting

**Notifications not showing?**
- Open **System Settings** → **Notifications**
- Find **AirTransfer** (or `org.python.python` if running raw script)
- Ensure **Allow Notifications** is ON.

**"Connection not private" warning?**
- You are likely running in HTTPS mode without a trusted cert on your phone.
- **Fix:** Use HTTP mode (delete `certs/` folder) OR follow the `gen_certs.sh` guide to trust the certificate.

## Project Structure

```
airtransfer/
├── app.py              # Main menu bar application (wrapper)
├── server.py           # Flask web server
├── start.sh            # Launcher script
├── build_app.sh        # Builds the .app bundle (py2app)
├── setup.py            # py2app configuration
├── templates/          # HTML UI
├── static/             # Icons & Assets
└── venv/               # Virtual Environment
```
