from PyInstaller.utils.hooks import collect_data_files

pykakasi_datas = collect_data_files(
    'pykakasi',
    includes=['data/*.db']
)

a = Analysis(
    ['inventory-management.py'],
    pathex=[],
    binaries=[],
    datas=pykakasi_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='inventory-management',
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
    icon=['inventory-management.ico'],
)
