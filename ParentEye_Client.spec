# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ParentEye Client EXE
Run with: pyinstaller ParentEye_Client.spec
"""

block_cipher = None

a = Analysis(
    ['client_exe.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('templates', 'templates'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'pymongo',
        'dotenv',
        'requests',
        'pynput',
        'psutil',
        'pyautogui',
        'cv2',
        'numpy',
        'imageio',
        'mss',
        'pygetwindow',
        'pyttsx3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        'matplotlib',
        'pandas',
        'scipy',
        'sklearn',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ParentEye',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # ⚠️ CRITICAL: Set to False to hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Optional: add icon path here like 'icon.ico'
)
