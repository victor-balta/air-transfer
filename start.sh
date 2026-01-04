#!/bin/bash
set -euo pipefail

# Run using the project's venv python directly.
# (Virtualenv "activate" scripts bake in absolute paths and break if the project folder is moved.)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

if [[ -x "$PROJECT_ROOT/venv/bin/python" ]]; then
  # If trusted certs exist, use them automatically.
  CERT_DEFAULT="$PROJECT_ROOT/certs/airtransfer-cert.pem"
  KEY_DEFAULT="$PROJECT_ROOT/certs/airtransfer-key.pem"
  if [[ -z "${AIRTRANSFER_CERT:-}" && -z "${AIRTRANSFER_KEY:-}" && -f "$CERT_DEFAULT" && -f "$KEY_DEFAULT" ]]; then
    export AIRTRANSFER_CERT="$CERT_DEFAULT"
    export AIRTRANSFER_KEY="$KEY_DEFAULT"
  else
     # Default to HTTP (Simple Mode) to avoid "Not Secure" warnings for generic usage.
     # Set AIRTRANSFER_USE_HTTP=0 to force HTTPS/PWA mode if you have a cert.
     export AIRTRANSFER_USE_HTTP="${AIRTRANSFER_USE_HTTP:-1}"
  fi
  
  # Check if the App Bundle exists and run via its launcher to get correct Dock/Notification icons.
  # This tricks macOS into thinking we are running the real App, not just Python.
  APP_LAUNCHER="$PROJECT_ROOT/dist/AirTransfer.app/Contents/MacOS/AirTransfer"
  if [[ -x "$APP_LAUNCHER" ]]; then
      # In py2app Alias mode, we need to ensure we run from the project root or handle paths correctly.
      # But py2app handles its own bootstrapping.
      exec "$APP_LAUNCHER"
  fi

  # Fallback to direct python execution if app build is missing
  exec "$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/app.py"
fi

echo "Error: venv not found at '$PROJECT_ROOT/venv'. Create it with:"
echo "  python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
exit 1
