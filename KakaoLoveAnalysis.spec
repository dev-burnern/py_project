# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['api.py'],
    pathex=[],
    binaries=[],
    datas=[('frontend/dist', 'frontend/dist'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\_wrap.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\template.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\_version.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\documentation.md', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\_c_api.pyi', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\_c_api.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\default_typo_transformer.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\__init__.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\sw_tokenizer.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\const.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\sw_trainer.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\transformers_addon.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\corpus\\stopwords.txt', 'kiwipiepy\\corpus'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\utils.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\knlm.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy\\__main__.py', 'kiwipiepy'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy-0.22.1.dist-info', 'kiwipiepy-0.22.1.dist-info'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\dialect.dict', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\default.dict', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\combiningRule.txt', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\extract.mdl', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\typo.dict', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\_version.py', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\sj.morph', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\cong.mdl', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\multi.dict', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model\\__init__.py', 'kiwipiepy_model'), ('C:\\Users\\삼성\\Desktop\\py_project\\.venv\\Lib\\site-packages\\kiwipiepy_model-0.22.0.dist-info', 'kiwipiepy_model-0.22.0.dist-info')],
    hiddenimports=['bottle', 'webview', 'clr', 'kiwipiepy', 'kiwipiepy.__main__', 'kiwipiepy._c_api', 'kiwipiepy._version', 'kiwipiepy._wrap', 'kiwipiepy.const', 'kiwipiepy.default_typo_transformer', 'kiwipiepy.knlm', 'kiwipiepy.sw_tokenizer', 'kiwipiepy.sw_trainer', 'kiwipiepy.template', 'kiwipiepy.transformers_addon', 'kiwipiepy.utils', 'kiwipiepy_model', 'kiwipiepy_model._version'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PIL', 'wordcloud', 'notebook', 'ipython', 'tkinter', 'reportlab', 'uvicorn', 'starlette', 'qrcode'],
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
    name='KakaoLoveAnalysis',
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
