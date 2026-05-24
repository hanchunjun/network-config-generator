# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('config', 'config')],
    hiddenimports=[
        'src.core.local_audit_engine', 'src.core.local_diagnostic_engine',
        'src.ui.subnet_calculator_page', 'src.ui.batch_cmd_generator_page',
        'src.core.account_manager', 'src.ui.login_dialog',
        'src.ui.account_manager_dialog',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'keras', 'torch', 'PySide6', 'IPython', 'pygame',
        'transformers', 'spacy', 'nltk', 'scipy', 'pandas', 'matplotlib',
        'sklearn', 'seaborn', 'plotly', 'bokeh', 'dash', 'cv2',
        'sqlalchemy', 'sympy', 'flask', 'django', 'fastapi', 'uvicorn',
        'beautifulsoup4', 'selenium', 'jupyter', 'nbformat', 'nbconvert',
        'openpyxl', 'tzdata', 'pydantic', 'rich', 'lxml', 'docutils',
        'grpc', 'zmq', 'h5py', 'onnxruntime',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NetworkConfigGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest='app.manifest',
)