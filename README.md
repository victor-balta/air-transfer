# AirTransfer 📡

**Transfer files from your Android/iOS phone to your Mac instantly over Wi-Fi.**

A lightweight, self-hosted alternative to AirDrop for Android ↔ Mac file transfers. No internet required, everything stays on your local network.

![AirTransfer Demo](https://via.placeholder.com/800x400?text=AirTransfer+Demo+Image)

## ✨ Features

- ⚡ **Instant Transfer**: Transfers files at your Wi-Fi's maximum speed.
- 📱 **PWA Support**: Install it as a native-like app on your phone's home screen.
- 🎯 **Share Target**: Share files directly from your phone's "Share" menu (Gallery, Files, etc.).
- 🔔 **Native Notifications**: Get macOS notifications with sound when files arrive.
- 💻 **Menu Bar App**: Runs quietly in your Mac's menu bar/tray.
- 🔒 **Private & Secure**: Data never leaves your local network.
- � **Modern UI**: meaningful animations and glassmorphism design.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- **macOS** (Required for the menu bar app and notifications)
- **Python 3.9** or higher
- Both devices must be on the **same Wi-Fi network**.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/airtransfer.git
   cd airtransfer
   ```

2. **Run the Setup Script**
   We've included a script that handles virtual environment creation and dependency installation for you.
   ```bash
   ./start.sh
   ```
   *Note: If you get a permission error, run `chmod +x start.sh` first.*

3. **That's it!** 
   - The server will start.
   - A **QR Code** will be printed in your terminal.
   - An icon (📡) will appear in your macOS menu bar.

---

## 📲 Connecting Your Phone

1. **Scan the QR Code** displayed in your terminal with your phone's camera.
   - Or manually enter the URL copied to your clipboard (e.g., `http://192.168.1.x:5002`).

2. **Send a File**
   - Tap the upload area to select files.
   - Or drag and drop files onto the screen.

### 🌟 Pro Tip: Install as an App (PWA)

For the best experience (including sharing directly from other apps), install AirTransfer to your home screen.

**On Android (Chrome):**
1. Tap the menu (**⋮**) > **Add to Home Screen** or **Install App**.
2. *Create a "Share Target"*:
   - If you want to share from your Gallery app, you might need to enable "Insecure origins treated as secure" for this URL in `chrome://flags` since this runs on HTTP (local network). 
   - *However, for basic file uploading via the browser, no special flags are needed.*

**On iOS (Safari):**
1. Tap the **Share** button (box with arrow).
2. Scroll down and tap **Add to Home Screen**.

---

## 📂 Where are my files?

All received files are automatically saved to your Mac's **Downloads** folder (`~/Downloads`).

You can quickly open this folder by clicking the 📡 icon in the menu bar and selecting **"Open Downloads"**.

---

## 🛠 Troubleshooting

**1. I can't connect from my phone.**
- Ensure both devices are on the **same Wi-Fi network**.
- Check your Mac's **Firewall** settings (System Settings > Network > Firewall). You may need to allow incoming connections for Python.
- If you are using a VPN on either device, try turning it off.

**2. The QR Code didn't appear.**
- The app prints the QR code to the terminal standard output. Check the terminal window where you ran `./start.sh`.
- You can also click the Menu Bar icon > **Show QR Code**.

**3. "Address already in use" error.**
- The app automatically tries to find an open port between 5002-5100. If it fails, try waiting a few seconds and running `./start.sh` again.

---

## 🏗 Architecture

```mermaid
graph LR
    Phone[Mobile Device] -- HTTP/Wi-Fi --> Flask[Flask Server (Mac)]
    Flask -- Save File --> FS[~/Downloads]
    Flask -- Trigger --> Rumps[Menu Bar App]
    Rumps -- Notify --> User[macOS Notification]
```

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla JS, CSS3 (Glassmorphism)
- **System Integration**: `rumps` (Menu Bar), `terminal-notifier` (Notifications)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
