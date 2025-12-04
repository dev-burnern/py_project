# ================================
# 가장 쉬운 Bottle 서버 예제 (초보자용)
# ================================

import os
from bottle import Bottle, run, request, response, static_file

# 내가 만든 분석 함수들
from backend.parser import parse_kakao_chat
from backend.analysis import (
    analyze_participation,
    extract_keywords,
    infer_love_insight,
    analyze_time_distribution,
)

app = Bottle()

# --------------------------------
# CORS 허용 (리액트에서 호출 가능하게)
# --------------------------------
@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"


# --------------------------------
# 분석 결과 만들어주는 간단한 함수
# --------------------------------
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
        "timeDistribution": time_dist
    }


# --------------------------------
# 텍스트 붙여넣기 분석 API
# --------------------------------
@app.post("/api/analyze_text")
def analyze_text():
    data = request.json or {}
    text = (data.get("text") or "").strip()

    if not text:
        response.status = 400
        return {"error": "텍스트가 없습니다."}

    # 임시 파일 저장
    os.makedirs("assets", exist_ok=True)
    temp_file = "assets/_temp.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(text)

    # 파싱
    df = parse_kakao_chat(temp_file)
    if df is None or df.empty:
        response.status = 400
        return {"error": "카톡 형식이 올바르지 않습니다."}

    return make_result(df)


# --------------------------------
# 리액트 빌드 파일 서빙
# --------------------------------
@app.route("/assets/<filepath:path>")
def serve_assets(filepath):
    return static_file(filepath, root="frontend/dist/assets")


@app.route("/")
@app.route("/<path:path>")
def serve_index(path=""):
    return static_file("index.html", root="frontend/dist")


# --------------------------------
# 서버 실행
# --------------------------------
if __name__ == "__main__":
    run(app, host="localhost", port=5000, debug=True)
