# api.py
import os
import sys
import base64
import threading
import webview  # pywebview 추가
from io import BytesIO

from bottle import Bottle, run, response, request, static_file
# from wordcloud import WordCloud  <-- 제거

from backend.parser import parse_kakao_chat
from backend.analysis import (
    analyze_participation,
    extract_keywords,
    infer_love_insight,
    analyze_time_distribution,
)

app = Bottle()

# ===== PyInstaller 경로 호환성 처리 =====
def resource_path(relative_path):
    """ PyInstaller로 패키징된 경우 임시 폴더(_MEIPASS)에서 리소스를 찾고, 아니면 현재 경로에서 찾음 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = (
        "Origin, Accept, Content-Type, X-Requested-With"
    )


def build_analysis_result(df):
    """
    공통 분석 로직: participation, keywords, 사랑의 큐피트 분석, 시간대 분석
    """
    participation = analyze_participation(df)
    keywords = extract_keywords(df, top_n=50)
    love = infer_love_insight(keywords)
    # wordcloud_data = make_wordcloud_base64(keywords) <-- 제거
    time_distribution = analyze_time_distribution(df)

    return {
        "participation": participation,
        "keywords": keywords[:10],  # 표시는 Top10만
        "totalMessages": len(df),
        # 사랑의 큐피트 전용 필드
        "interestScore": love["interestScore"],
        "interestLabel": love["interestLabel"],
        "topic": love["topic"],        # 한 줄 요약
        "summary": love["summary"],    # 긴 설명
        # "wordcloud": wordcloud_data,   <-- 제거
        "timeDistribution": time_distribution,  # ← 시간대별 대화량
    }


# ===== (기존) 파일 기반 분석: assets/chat.txt 사용 =====
@app.get("/api/analyze")
def analyze_file():
    # 실행 파일 옆에 있는 assets 폴더를 참조하도록 설정
    filepath = os.path.join(os.getcwd(), "assets", "chat.txt")

    if not os.path.exists(filepath):
        response.status = 400
        return {"error": "assets/chat.txt 파일을 찾을 수 없습니다."}

    try:
        df = parse_kakao_chat(filepath)
    except Exception as e:
        response.status = 400
        return {"error": f"대화 내용을 읽는 도중 오류가 발생했습니다: {e}"}

    if df.empty:
        response.status = 400
        return {"error": "대화 내용을 읽지 못했습니다."}

    return build_analysis_result(df)


# ===== (신규) 사이트 내 텍스트 입력 분석 =====
@app.post("/api/analyze_text")
def analyze_text():
    data = request.json or {}
    raw_text = (data.get("text") or "").strip()

    if not raw_text:
        response.status = 400
        return {"error": "분석할 대화 내용을 입력해주세요."}

    # 실행 위치 기준 assets 폴더 사용
    os.makedirs("assets", exist_ok=True)
    temp_path = os.path.join("assets", "_temp_input.txt")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        df = parse_kakao_chat(temp_path)
    except Exception as e:
        response.status = 400
        return {"error": f"대화 내용을 파싱하는 중 문제가 발생했습니다: {e}"}

    if df.empty:
        response.status = 400
        return {
            "error": "대화 내용을 하나도 읽지 못했습니다. 카카오톡 내보내기 원본 형식인지 확인해주세요."
        }

    return build_analysis_result(df)


# ===== 정적 파일 서빙 (React 빌드 결과물) =====
@app.route('/assets/<filepath:path>')
def server_static(filepath):
    # frontend/dist/assets 폴더 서빙
    return static_file(filepath, root=resource_path(os.path.join('frontend', 'dist', 'assets')))

@app.route('/')
@app.route('/<path:path>')
def serve_index(path=""):
    # 그 외 모든 요청은 index.html (SPA 라우팅)
    return static_file("index.html", root=resource_path(os.path.join('frontend', 'dist')))


def start_server():
    # Bottle 서버 실행 (메인 스레드 차단 방지를 위해 별도 함수로 분리)
    run(app, host="localhost", port=5000, debug=False, reloader=False)

if __name__ == "__main__":
    # 1. 서버 스레드 시작
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # 2. PyWebView 창 생성 및 시작 (메인 스레드에서 실행해야 함)
    webview.create_window(
        "Kakao Love Analysis", 
        "http://localhost:5000",
        width=1200,
        height=900,
        resizable=True
    )
    webview.start()
