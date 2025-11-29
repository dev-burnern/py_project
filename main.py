import os
from backend.parser import parse_kakao_chat
from backend.analysis import analyze_participation, extract_keywords, infer_topic

def main():
    # 1. 분석할 파일 경로 설정
    # (파일이 assets 폴더 안에 있는지 확인해주세요)
    filepath = "assets/chat.txt"

    print(f"=== 📂 '{filepath}' 데이터 읽기 시작 ===")

    # [안전장치 1] 파일이 실제로 존재하는지 확인
    if not os.path.exists(filepath):
        print(f"\n[오류] 파일을 찾을 수 없습니다: {filepath}")
        print("👉 'assets' 폴더를 만들고 그 안에 'chat.txt' 파일을 넣어주세요.")
        return

    # 2. 파싱 (텍스트 -> 데이터프레임 변환)
    try:
        df = parse_kakao_chat(filepath)
    except Exception as e:
        print(f"\n[오류] 파일을 읽는 도중 문제가 발생했습니다: {e}")
        return

    # [안전장치 2] 파싱 결과가 비어있는지 확인
    if df.empty:
        print("\n[주의] 대화 내용을 하나도 읽지 못했습니다.")
        print("1. 파일 내용이 비어있는지 확인해보세요.")
        print("2. 카카오톡 '내보내기'한 원본 파일이 맞는지 확인해주세요.")
        return

    print(f"✅ 파싱 완료! 총 {len(df)}개의 메시지를 분석합니다.")
    print("-" * 40)

    # 3. 참여율 분석
    print("\n📊 [참여자별 발화량]")
    participation = analyze_participation(df)
    for rank, p in enumerate(participation, 1):
        # 보기 좋게 출력 (예: 1. 홍길동: 100회 (25.5%))
        print(f"{rank}. {p['sender']}: {p['count']}회 ({p['ratio']}%)")

    # 4. 키워드 분석 (Kiwi + Scikit-learn)
    print("\n🔑 [핵심 키워드 Top 10]")
    keywords = extract_keywords(df, top_n=10)
    
    if keywords:
        for i, k in enumerate(keywords, 1):
            print(f"{i}. {k['word']} ({k['count']}회)")
    else:
        print("👉 분석할 만한 명사가 충분하지 않습니다.")

    # 5. 주제 추론
    print("\n💡 [대화 주제 추론]")
    topic = infer_topic(keywords)
    print(f"👉 분석 결과, 이 대화방은 '{topic}' 성향이 강합니다.")

if __name__ == "__main__":
    main()