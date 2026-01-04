#!/bin/bash
set -e

APP_NAME="AirTransfer"
ICON_SOURCE="static/app_icon.png"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
MACOS_DIR="$CONTENTS_DIR/MacOS"

echo "Building $APP_NAME.app..."

# 1. Create Directory Structure
rm -rf "$APP_BUNDLE"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# 2. Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.victorbalta.airtransfer</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# 3. Create Launcher Script
# We need a wrapper to set up the environment and run python
cat > "$MACOS_DIR/launcher" <<EOF
#!/bin/bash
DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
# Go up 4 levels: MacOS -> Contents -> AirTransfer.app -> dist -> ProjectRoot
PROJECT_ROOT="\$(cd "\$DIR/../../../.." && pwd)"
cd "\$PROJECT_ROOT"

# Prefer the project's venv python directly.
# (Virtualenv "activate" scripts bake in absolute paths and break if the project folder is moved.)
if [ -x "venv/bin/python" ]; then
    PYTHON_BIN="venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# EXECUTE using the Python interpreter but ensuring we are inside the bundle context
exec "$PYTHON_BIN" "app.py"
EOF

chmod +x "$MACOS_DIR/launcher"

# 4. Generate ICNS Icon
if [ -f "$ICON_SOURCE" ]; then
    echo "Generating AppIcon.icns..."
    ICONSET_DIR="AppIcon.iconset"
    mkdir -p "$ICONSET_DIR"

    # Create various sizes
    sips -z 16 16     "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16.png"
    sips -z 32 32     "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16@2x.png"
    sips -z 32 32     "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32.png"
    sips -z 64 64     "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32@2x.png"
    sips -z 128 128   "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128.png"
    sips -z 256 256   "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128@2x.png"
    sips -z 256 256   "$ICON_SOURCE" --out "$ICONSET_DIR/icon_256x256.png"
    sips -z 512 512   "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512@2x.png"
    sips -z 512 512   "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512.png"
    sips -z 1024 1024 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512@2x.png"

    iconutil -c icns "$ICONSET_DIR" -o "$RESOURCES_DIR/AppIcon.icns"
    rm -rf "$ICONSET_DIR"
else
    echo "Warning: $ICON_SOURCE not found. App will have default icon."
fi

echo "Done! App built at $APP_BUNDLE"
echo "To run: open $APP_BUNDLE"
