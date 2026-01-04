#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if ! command -v mkcert >/dev/null 2>&1; then
  echo "mkcert not found."
  echo "Install it with: brew install mkcert"
  exit 1
fi

IP="$("$PROJECT_ROOT/venv/bin/python" -c "import server; print(server.get_ip_address())" 2>/dev/null || true)"
if [[ -z "${IP}" ]]; then
  echo "Could not auto-detect LAN IP."
  echo "Run: ./venv/bin/python -c \"import server; print(server.get_ip_address())\""
  exit 1
fi

mkdir -p certs

CERT_FILE="certs/airtransfer-cert.pem"
KEY_FILE="certs/airtransfer-key.pem"

echo "Generating cert for: $IP (plus localhost)"
mkcert -cert-file "$CERT_FILE" -key-file "$KEY_FILE" "$IP" localhost 127.0.0.1 ::1

echo
echo "Generated:"
echo "  $CERT_FILE"
echo "  $KEY_FILE"
echo
echo "IMPORTANT (one-time, per device): install the mkcert root CA on your Android phone"
echo "  CA folder: $(mkcert -CAROOT)"
echo "  Copy 'rootCA.pem' to the phone, then:"
echo "    Android Settings -> Security -> Encryption & credentials -> Install a certificate -> CA certificate"
echo
echo "To run server with the trusted cert:"
echo "  ./venv/bin/python server.py --cert \"$CERT_FILE\" --key \"$KEY_FILE\""
echo
echo "To run menu bar app using these certs:"
echo "  AIRTRANSFER_CERT=\"$CERT_FILE\" AIRTRANSFER_KEY=\"$KEY_FILE\" ./start.sh"


