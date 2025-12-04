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


@app.route("/assets/<filepath:path>")
def serve_assets(filepath):
    return static_file(filepath, root="frontend/dist/assets")


@app.route("/")
@app.route("/<path:path>")
def serve_index(path=""):
    return static_file("index.html", root="frontend/dist")


if __name__ == "__main__":
    run(app, host="localhost", port=5000, debug=True)
