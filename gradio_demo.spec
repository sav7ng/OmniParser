# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

pathex=['E:\OmniParser']
datas = []
datas += collect_data_files('gradio_client')
datas += collect_data_files('gradio')
datas += collect_data_files('torch')

a = Analysis(
    ['gradio_demo.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['torch', 'torchvision', 'gradio', 'gradio_client'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    module_collection_mode={ 'gradio': 'py',},
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gradio_demo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gradio_demo',
)
