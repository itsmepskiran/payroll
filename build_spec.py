import os
import sys
import PyQt6
from PyQt6.QtCore import QLibraryInfo
from pathlib import Path

def create_spec():
    # Get PyQt6 installation directory using pathlib for proper path handling
    pyqt6_dir = Path(PyQt6.__file__).parent
    plugins_dir = pyqt6_dir / 'Qt6' / 'plugins'
    translations_dir = pyqt6_dir / 'Qt6' / 'translations'

    # Convert paths to forward slashes for the spec file
    plugins_path = plugins_dir.as_posix()
    translations_path = translations_dir.as_posix()

    # Create the spec file content
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py', 'login.py', 'main_window.py', 'database_setup.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('documents', 'documents'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSql',
        'PyQt6.QtNetwork',
        'pandas',
        'openpyxl',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
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
    name='HRMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    # Write the spec file
    with open('hrms_final.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("Spec file created successfully!")

if __name__ == '__main__':
    create_spec()