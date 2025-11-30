# api.py
import os
import base64
from io import BytesIO

from bottle import Bottle, run, response
from wordcloud import WordCloud

from backend.parser import parse_kakao_chat
from backend.analysis import analyze_participation, extract_keywords, infer_topic

app = Bottle()

# ===== 한글 워드클라우드용 폰트 경로 (윈도우 기준) =====
FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
if not os.path.exists(FONT_PATH):
    # 폰트 못 찾으면 None -> 한글이 깨질 수는 있지만 코드가 죽지는 않게
    FONT_PATH = None


# ===== CORS 허용 (Vite 프론트에서 호출 가능하도록) =====
@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type, X-Requested-With"


def make_wordcloud_base64(keywords):
    """
    keywords: [{ "word": str, "count": int }, ...]
    -> data:image/png;base64,.... 형태 문자열 반환
    """
    if not keywords:
        return None

    freqs = {k["word"]: k["count"] for k in keywords}
    if not freqs:
        return None

    # 워드클라우드 생성
    wc = WordCloud(
        font_path=FONT_PATH,
        width=800,
        height=400,
        background_color="white",
    ).generate_from_frequencies(freqs)

    img = wc.to_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


@app.get("/api/analyze")
def analyze():
    filepath = os.path.join("assets", "chat.txt")

    if not os.path.exists(filepath):
        response.status = 400
        return {"error": "assets/chat.txt 파일을 찾을 수 없습니다."}

    df = parse_kakao_chat(filepath)
    if df.empty:
        response.status = 400
        return {"error": "대화 내용을 읽지 못했습니다."}

    participation = analyze_participation(df)
    keywords = extract_keywords(df, top_n=50)  # 워드클라우드용으로 조금 더 많이
    topic = infer_topic(keywords)
    wordcloud_data = make_wordcloud_base64(keywords)

    return {
        "participation": participation,
        "keywords": keywords[:10],  # 표시는 Top10만
        "topic": topic,
        "totalMessages": len(df),
        "wordcloud": wordcloud_data,  # ← 프론트에서 <img src=...>로 사용
    }


if __name__ == "__main__":
    run(app, host="localhost", port=5000, debug=True, reloader=True)
