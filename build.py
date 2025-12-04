import PyInstaller.__main__
import os
from PyInstaller.utils.hooks import collect_all

# frontend/dist 폴더 확인
if not os.path.exists(os.path.join("frontend", "dist")):
    print("오류: frontend/dist 폴더가 없습니다. frontend 폴더에서 'npm run build'를 먼저 실행해주세요.")
    exit(1)

print("=== PyInstaller 빌드 시작 (PyWebView + Kiwi) ===")
print("React 빌드 파일과 Python 백엔드를 하나로 묶습니다...")

# kiwipiepy 및 모델 데이터 수집
tmp_ret = collect_all('kiwipiepy')
datas, binaries, hiddenimports = tmp_ret[0], tmp_ret[1], tmp_ret[2]

tmp_ret2 = collect_all('kiwipiepy_model')
datas += tmp_ret2[0]
binaries += tmp_ret2[1]
hiddenimports += tmp_ret2[2]

# PyInstaller 인자 생성
args = [
    'api.py',
    '--name=KakaoLoveAnalysis',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--add-data=frontend/dist;frontend/dist',
    '--hidden-import=bottle',
    '--hidden-import=webview',
    '--hidden-import=clr',
    '--noconsole',
    # 불필요한 패키지 제외 (용량 최적화)
    '--exclude-module=matplotlib',
    '--exclude-module=PIL',
    '--exclude-module=wordcloud',
    '--exclude-module=notebook',
    '--exclude-module=ipython',
    '--exclude-module=tkinter',
    '--exclude-module=reportlab',
    '--exclude-module=uvicorn',
    '--exclude-module=starlette',
    '--exclude-module=qrcode',
]

# 수집된 데이터 및 히든 임포트 추가
for s, d in datas:
    args.append(f'--add-data={s};{d}')

for h in hiddenimports:
    args.append(f'--hidden-import={h}')

PyInstaller.__main__.run(args)

print("\n=== 빌드 완료 ===")
print("dist/KakaoLoveAnalysis.exe 파일을 확인해주세요.")
