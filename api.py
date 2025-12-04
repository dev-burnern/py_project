import os
from bottle import Bottle, run, request, response, static_file

from backend.parser import parse_kakao_chat
from backend.analysis import (
    analyze_participation,
    extract_keywords,
    infer_love_insight,
    analyze_time_distribution,
)

app = Bottle()


@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"


def make_result(df):
    participation = analyze_participation(df)
    keywords = extract_keywords(df, top_n=50)
    love = infer_love_insight(keywords)
    time_dist = analyze_time_distribution(df)

    return {
        "participation": participation,
        "keywords": keywords[:10],
        "totalMessages": len(df),
        "interestScore": love["interestScore"],
        "interestLabel": love["interestLabel"],
        "topic": love["topic"],
        "summary": love["summary"],
        "timeDistribution": time_dist,
    }


@app.post("/api/analyze_text")
def analyze_text():
    data = request.json or {}
    text = (data.get("text") or "").strip()

    if not text:
        response.status = 400
        return {"error": "텍스트가 없습니다."}

    os.makedirs("assets", exist_ok=True)
    temp_file = "assets/_temp.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(text)

    df = parse_kakao_chat(temp_file)
    if df is None or df.empty:
        response.status = 400
        return {"error": "카톡 형식이 올바르지 않습니다."}

    return make_result(df)


# --------------------------------
# 리액트 빌드 파일 서빙
# --------------------------------
# PyInstaller로 패키징 시 경로 문제 해결
if getattr(sys, "frozen", False):
    # 실행 파일로 실행 중일 때 (임시 폴더 경로 사용)
    base_path = sys._MEIPASS
else:
    # 파이썬 스크립트로 실행 중일 때
    base_path = os.path.dirname(os.path.abspath(__file__))

@app.route("/assets/<filepath:path>")
def serve_assets(filepath):
    return static_file(filepath, root=os.path.join(base_path, "frontend/dist/assets"))


@app.route("/")
@app.route("/<path:path>")
def serve_index(path=""):
    return static_file("index.html", root=os.path.join(base_path, "frontend/dist"))


# --------------------------------
# 서버 실행
# --------------------------------
def start_server():
    run(app, host="localhost", port=5000, quiet=True)

if __name__ == "__main__":
    import threading
    import webview
    import sys

    # 1. 서버를 별도 스레드에서 실행
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # 2. PyWebView 창 열기 (메인 스레드)
    webview.create_window("카카오톡 대화 분석기 💘", "http://localhost:5000", width=1200, height=800)
    webview.start()
