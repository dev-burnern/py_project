# main.py
from backend.parser import parse_kakao_chat
from backend.analysis import analyze_participation, extract_keywords, infer_topic

df = parse_kakao_chat("assets/chat.txt")  # 📌 너가 넣을 파일 경로
print(df.head())

part = analyze_participation(df)
print("▶ 발화량 분석:", part)

keywords = extract_keywords(df)
print("▶ 키워드:", keywords)

topic = infer_topic(keywords)
print("▶ 주제:", topic)
