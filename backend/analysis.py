import pandas as pd
from kiwipiepy import Kiwi  # Java 없는 한국어 형태소 분석기
from sklearn.feature_extraction.text import CountVectorizer # 통계 분석용

# 1. Kiwi 초기화 (Java 설치 불필요, 속도 빠름)
try:
    kiwi = Kiwi()
except Exception as e:
    print(f"[오류] Kiwi 모듈을 불러오지 못했습니다. 'pip install kiwipiepy'를 확인하세요. ({e})")
    kiwi = None

# 2. 분석에서 제외할 불용어(Stopwords) 정의
# 의미 없는 감탄사나 조사를 걸러냅니다.
STOPWORDS = {
    "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "이거", "저거", "그거", "근데", 
    "진짜", "너무", "아니", "이제", "오늘", "내일", "그냥",
    "사람", "생각", "좀", "나", "너", "우리", "사진"
}

def analyze_participation(df: pd.DataFrame):
    """
    참여자별 발화 횟수와 비율을 계산합니다.
    """
    if df.empty:
        return []

    counts = df['sender'].value_counts()
    total = len(df)
    
    return [
        {
            "sender": sender, 
            "count": int(cnt), 
            "ratio": round(cnt / total * 100, 1)
        }
        for sender, cnt in counts.items()
    ]

def extract_keywords(df: pd.DataFrame, top_n: int = 20):
    """
    Kiwi로 명사를 추출하고 Scikit-learn으로 빈도를 계산하여
    상위 키워드를 반환합니다.
    """
    if df.empty or kiwi is None:
        return []

    # 메시지 컬럼을 문자열 리스트로 변환 (결측치 제거)
    messages = df['message'].dropna().astype(str).tolist()
    
    if not messages:
        return []

    # --- [핵심] 사이킷런에 연결할 커스텀 토크나이저 ---
    def kiwi_tokenizer(text):
        tokens = kiwi.tokenize(text)
        # NNG(일반명사), NNP(고유명사)만 추출 + 1글자 제외 + 불용어 제외
        return [
            t.form for t in tokens 
            if t.tag.startswith('NN') and len(t.form) > 1 and t.form not in STOPWORDS
        ]

    # CountVectorizer 설정
    # max_features: 상위 N개만 추출 (속도 최적화)
    vectorizer = CountVectorizer(tokenizer=kiwi_tokenizer, max_features=top_n)
    
    try:
        # 단어 빈도 행렬 생성 (Fit & Transform)
        X = vectorizer.fit_transform(messages)
        
        # 결과 매핑 (단어: 빈도수)
        feature_names = vectorizer.get_feature_names_out()
        word_counts = X.sum(axis=0).tolist()[0]
        
        keywords = []
        for word, count in zip(feature_names, word_counts):
            keywords.append({"word": word, "count": int(count)})
        
        # 빈도수 내림차순 정렬
        keywords.sort(key=lambda x: x['count'], reverse=True)
        return keywords

    except ValueError:
        # 텍스트가 너무 적거나 분석할 명사가 없을 경우
        return []
    except Exception as e:
        print(f"[키워드 추출 오류] {e}")
        return []

def infer_topic(keywords):
    """
    추출된 키워드를 기반으로 대화방의 주제를 단순 추론합니다.
    """
    if not keywords:
        return "데이터 부족 / 알 수 없음"

    words = {k['word'] for k in keywords}
    
    # 주제별 키워드 사전
    topics = {
        "학업/과제": {"과제", "발표", "교수님", "시험", "공부", "강의", "팀플", "제출"},
        "식사/약속": {"치킨", "약속", "모임", "술", "맥주", "맛집", "카페", "저녁", "점심"},
        "개발/코딩": {"코드", "에러", "파이썬", "개발", "배포", "서버", "함수", "변수"},
        "주식/투자": {"주식", "코인", "매수", "매도", "떡상", "떡락", "비트코인"}
    }

    # 교집합이 있는지 확인
    for topic_name, topic_words in topics.items():
        if topic_words & words: # 교집합이 하나라도 있으면
            return f"{topic_name} 관련"
            
    return "일상 대화 중심"