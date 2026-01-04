from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    'static',
    'templates',
    'certs'
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'static/app_icon.icns',
    'plist': {
        'CFBundleName': 'AirTransfer',
        'CFBundleDisplayName': 'AirTransfer',
        'CFBundleGetInfoString': "AirTransfer File Receiver",
        'CFBundleIdentifier': "com.victorbalta.airtransfer",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'LSUIElement': True, # Agent app (no dock icon usually, but we forced it in code. Set False if you want standard Dock app)
    },
    'packages': ['rumps', 'flask', 'qrcode', 'PIL', 'netifaces', 'OpenSSL'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

