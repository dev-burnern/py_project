import PyInstaller.__main__
import os

# frontend/dist 폴더 확인
if not os.path.exists(os.path.join("frontend", "dist")):
    print("오류: frontend/dist 폴더가 없습니다. frontend 폴더에서 'npm run build'를 먼저 실행해주세요.")
    exit(1)

print("=== PyInstaller 빌드 시작 (PyWebView) ===")
print("React 빌드 파일과 Python 백엔드를 하나로 묶습니다...")

PyInstaller.__main__.run([
    'api.py',
    '--name=KakaoLoveAnalysis',
    '--onefile',
    '--clean',
    '--noconfirm',
    # frontend/dist 폴더를 실행 파일 내부의 frontend/dist로 포함
    '--add-data=frontend/dist;frontend/dist',
    # 필요한 라이브러리 명시적 포함
    '--hidden-import=bottle',
    '--hidden-import=webview',  # pywebview 추가
    '--hidden-import=clr',      # pythonnet (Windows용)
    # 콘솔 창 숨기기 (GUI 모드)
    '--noconsole', 
])

print("\n=== 빌드 완료 ===")
print("dist/KakaoLoveAnalysis.exe 파일을 확인해주세요.")
