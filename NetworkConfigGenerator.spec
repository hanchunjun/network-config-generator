# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('config', 'config'), ('agents', 'agents')],
    hiddenimports=[
        'src.core.local_audit_engine', 'src.core.local_diagnostic_engine',
        'src.core.theme_engine',
        'src.ui.subnet_calculator_page', 'src.ui.batch_cmd_generator_page',
        'src.ui.theme_switcher_page',
        'src.core.account_manager', 'src.ui.login_dialog',
        'src.ui.account_manager_dialog',
        'src.ui.single_device.compliancecheckthread',
        'src.ui.single_device.aidiagnosticthread',
        'src.ui.single_device.singledeviceworker',
        'src.ui.single_device.deviceformdialog',
        'src.ui.config_pages.templates.ruijie_cli',
        'src.ui.config_pages.templates.huawei_cli',
        'src.ui.config_pages.templates.h3c_cli',
        'src.ui.config_pages.templates.cisco_cli',
        'src.utils.app_factory',
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
        # PyQt5 未使用子模块（减小 EXE 体积 10~20MB）
        'PyQt5.QtSql', 'PyQt5.QtOpenGL', 'PyQt5.QtSvg', 'PyQt5.QtTest',
        'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets', 'PyQt5.QtBluetooth',
        'PyQt5.QtPositioning', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort',
        'PyQt5.QtWinExtras', 'PyQt5.QtMacExtras', 'PyQt5.QtX11Extras',
        'PyQt5.QtAndroidExtras',
        # 死依赖清理
        'bcrypt',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NetOps',
    debug=False,
    icon='assets/netops.ico',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetOps',
)