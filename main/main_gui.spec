# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\UI', 'UI'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\Collect', 'Collect'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\Registry_collector', 'Registry_collector'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\gui_tk.py', '.'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\쪼랭이.py', '.'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\eventlog', 'eventlog'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\NTFS', 'NTFS'), ('C:\\Users\\ADMIN\\Desktop\\Artifact-Collector-main\\main\\volatility_data', 'volatility_data')],
    hiddenimports=['sip'],
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
    name='main_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
