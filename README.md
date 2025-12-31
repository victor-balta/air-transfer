# AirTransfer

**Transfer files from your Android phone to your Mac instantly over Wi-Fi.**

A lightweight, self-hosted alternative to AirDrop for Android ↔ Mac file transfers.

## Features

- 📱 **PWA Support** - Add to home screen for one-tap access
- 🎯 **Android Share Target** - Share directly from any app
- 🔔 **Native Notifications** - Get notified when files arrive
- 🎨 **Modern UI** - Beautiful glassmorphism design
- ⚡ **Fast** - Transfers at your Wi-Fi's max speed
- 🔒 **Private** - Everything stays on your local network

## Quick Start

### 1. Start the Server
```bash
cd ~/Desktop/Projects/airdrop-clone
./start.sh
```

### 2. Connect Your Phone (First Time)
1. Scan the QR code that appears in your terminal
2. **Important:** You will see a "Not Secure" or "Privacy Error" warning.
   - This is normal because we are using a self-signed certificate for local security.
   - Click **Advanced** → **Proceed to... (unsafe)**
3. When prompted, tap "Add to Home Screen" or "Install App"
4. You now have an **AirTransfer** app icon!

### 3. Send Files
**Option A: From the App**
- Open AirTransfer from your home screen
- Tap to select files or drag & drop

**Option B: From Any App (Share)**
- Open Gallery, Files, or any app
- Tap Share → Select "AirTransfer"
- Files go directly to your Mac!

## Files Location

All received files are saved to: `~/Downloads`

## Architecture

```
┌──────────────────┐         Wi-Fi          ┌──────────────────┐
│   Samsung S23    │◄──────────────────────►│    Mac Air M4    │
│                  │                         │                  │
│  Browser (PWA)   │────── HTTP POST ──────►│  Flask Server    │
│  Share Target    │                         │  (server.py)     │
└──────────────────┘                         └──────────────────┘
                                                     │
                                                     ▼
                                              ~/Downloads/
```

## Project Structure

```
airdrop-clone/
├── app.py              # Menu bar app entry point
├── server.py           # Flask web server
├── start.sh            # Startup script
├── templates/
│   └── index.html      # Mobile web UI
├── static/
│   ├── manifest.json   # PWA configuration
│   ├── sw.js           # Service worker
│   └── icon-*.png      # App icons
└── venv/               # Python virtual environment
```

## Requirements

- Python 3.9+
- macOS (for menu bar app)
- Both devices on the same Wi-Fi network

## Dependencies

```
flask
qrcode
netifaces
rumps
Pillow
```

Install: `pip install -r requirements.txt`

## Troubleshooting

**No notification sound?**
- Check System Settings → Notifications → terminal-notifier
- Ensure Do Not Disturb is off

**Can't connect from phone?**
- Both devices must be on the same Wi-Fi
- Check your firewall settings

**Port already in use?**
- The app automatically tries ports 5000-5099
