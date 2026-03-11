# ══════════════════════════════════════════════════════════════════════════════
#  stockmate.spec — PyInstaller build configuration
#  Run with:  pyinstaller stockmate.spec
# ══════════════════════════════════════════════════════════════════════════════

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Grab all customtkinter assets (images, themes, fonts)
ctk_datas = collect_data_files("customtkinter")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        *ctk_datas,                    # customtkinter themes & assets
        ("pages/*.py",   "pages"),     # our pages package
    ],
    hiddenimports=[
        "customtkinter",
        "PIL",
        "PIL._tkinter_finder",
        "tkinter",
        "tkinter.ttk",
        "sqlite3",
        "pages.lowstock",
        "pages.activity",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="StockMate",           # .exe filename
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                   # compress the exe (smaller file)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # no black terminal window behind the app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="icon.ico",          # uncomment & add icon.ico to use a custom icon
)
