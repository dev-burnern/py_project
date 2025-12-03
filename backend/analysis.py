import pandas as pd
from kiwipiepy import Kiwi  # Java 없는 한국어 형태소 분석기
from sklearn.feature_extraction.text import CountVectorizer  # 통계 분석용

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

    counts = df["sender"].value_counts()
    total = len(df)

    return [
        {
            "sender": sender,
            "count": int(cnt),
            "ratio": round(cnt / total * 100, 1),
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
    messages = df["message"].dropna().astype(str).tolist()

    if not messages:
        return []

    # --- [핵심] 사이킷런에 연결할 커스텀 토크나이저 ---
    def kiwi_tokenizer(text):
        tokens = kiwi.tokenize(text)
        # NNG(일반명사), NNP(고유명사)만 추출 + 1글자 제외 + 불용어 제외
        return [
            t.form
            for t in tokens
            if t.tag.startswith("NN")
            and len(t.form) > 1
            and t.form not in STOPWORDS
        ]

    # CountVectorizer 설정
    # max_features: 상위 N개만 추출 (속도 최적화)
    vectorizer = CountVectorizer(tokenizer=kiwi_tokenizer, max_features=top_n)

    # 단어 빈도 행렬 생성 (Fit & Transform)
    try:
        X = vectorizer.fit_transform(messages)
        feature_names = vectorizer.get_feature_names_out()

        # sparse matrix sum을 안정적으로 1차원 리스트로 변환
        sums = X.sum(axis=0)
        try:
            # scipy/numpy matrix에 따라 .A1 속성이 존재할 수 있음
            word_counts = sums.A1
        except Exception:
            # fallback: list 형태로 변환
            word_counts = sums.tolist()[0]

    except ValueError:
        # 텍스트가 너무 적거나 분석할 명사가 없을 경우
        return []
    except Exception as e:
        # 예기치 못한 토크나이저/벡터라이저 오류 로깅 후 빈 결과 반환
        print(f"[키워드 추출 오류] {e}")
        return []

    keywords = []
    for word, count in zip(feature_names, word_counts):
        keywords.append({"word": word, "count": int(count)})

    # 빈도수 내림차순 정렬
    keywords.sort(key=lambda x: x["count"], reverse=True)
    return keywords


def analyze_time_distribution(df: pd.DataFrame):
    """
    카톡 대화가 어느 시간대(0~23시)에 가장 많이 오갔는지 분석합니다.
    실제 '답장 딜레이'까지 보진 않고,
    메시지가 많이 오간 시간대를 '활발한 시간대'로 사용합니다.
    """
    if df.empty:
        return []

    dt_series = None

    # parser가 어떤 컬럼명을 쓰는지 몰라서 안전하게 처리
    if "datetime" in df.columns:
        dt_series = pd.to_datetime(df["datetime"], errors="coerce")
    elif "time" in df.columns:
        dt_series = pd.to_datetime(df["time"], errors="coerce")
    else:
        return []

    dt_series = dt_series.dropna()
    if dt_series.empty:
        return []

    counts = dt_series.dt.hour.value_counts().sort_index()

    # 0~23시까지 전부 포함해서 리턴 (없는 시간대는 0으로)
    result = []
    for hour in range(24):
        cnt = int(counts.get(hour, 0))
        result.append({"hour": hour, "count": cnt})
    return result


def infer_love_insight(keywords):
    """
    추출된 키워드를 기반으로 '호감도/관심도'를 추론합니다.
    (사랑의 큐피트 버전)
    """
    if not keywords:
        return {
            "interestScore": 0,
            "interestLabel": "데이터 부족 😢",
            "topic": "대화량이 너무 적어서 마음을 읽기 어려워요.",
            "summary": "조금 더 대화를 나누고 다시 분석해보는 건 어때요?",
        }

    # 키워드 목록에서 단어 집합 생성 (중복 제거)
    words = {k["word"] for k in keywords}

    # 연애/호감 관련 키워드들 (굉장히 러프한 휴리스틱)
    strong_love_words = {
        "사랑", "사랑해", "좋아해", "너밖에", "보고싶", "보고싶다",
        "보고 싶다", "설레", "썸", "심쿵", "고백", "사귀자", "연애"
    }
    light_love_words = {
        "귀엽", "귀여워", "이쁘다", "예쁘다", "잘생겼", "멋있다",
        "데이트", "영화", "밥먹자", "밥이나", "술한잔", "술 한잔",
        "만날까", "보자", "만나자"
    }
    contact_words = {
        "카톡", "톡", "연락", "전화", "심심", "보고싶네", "만나",
        "언제", "시간", "약속", "주말"
    }
    cold_words = {
        "바빠", "피곤", "나중에", "귀찮", "힘들", "관심없", "됐어",
        "그만", "몰라", "싫어", "안돼"
    }

    # ✅ 단어 그룹별 "히트 개수" 계산 (단어 종류 수 기준)
    strong_hits = len(words & strong_love_words)
    light_hits = len(words & light_love_words)
    contact_hits = len(words & contact_words)
    cold_hits = len(words & cold_words)

    # ✅ 점수 계산: 기본 50에서 가산/감점 (더 공격적으로 조정)
    score = 50
    score += 18 * strong_hits      # 강한 애정 표현이면 크게 플러스
    score += 10 * light_hits       # 가벼운 호감/칭찬
    score += 4 * contact_hits      # 연락/만남 시도

    # ❗ 부정 키워드는 훨씬 세게 깎음
    score -= 25 * cold_hits        # 한 종류만 있어도 25점↓, 두 개면 사실상 바닥

    # 0 ~ 100 사이로 클램핑
    score = max(0, min(100, score))

    # 점수 구간별 라벨링
    if score >= 80:
        label = "저 몰래 두분 이미 사귀고 있죠? 💘"
        topic = "상당히 달달한 분위기! 서로 마음이 통하는 느낌이에요 남은 건 고백 뿐!."
        summary = (
            "대화에 애정 표현이나 만남 제안, 설레는 뉘앙스가 많이 보여요. "
            "상대방이 당신에게 꽤 많은 호감을 가지고 있을 가능성이 높아요!"
        )
    elif score >= 60:
        label = "호감 있는 편 💗"
        topic = "친근함 속에 묘한 설렘이 느껴지는 대화네요."
        summary = (
            "친근한 농담과 가벼운 애정 표현, 만남 이야기가 자연스럽게 오가는 편이에요. "
            "서로 눈치를 보는 단계일 수 있고, 잘 이어가면 썸으로 발전할 수도 있어요!"
        )
    elif score >= 40:
        label = "친한 친구 느낌 😊"
        topic = "편하고 재밌는 친구 느낌의 대화가 많아요."
        summary = (
            "일상 대화와 가벼운 농담 위주라 분위기는 좋지만, 아직 뚜렷한 연애 뉘앙스는 적어요. "
            "조금 더 솔직한 표현이나 개인적인 이야기들을 던져보는 건 어떨까요?"
        )
    else:
        label = "연애 감정은 낮은 편 😶"
        topic = "아직은 관계를 지켜보는 단계처럼 보여요."
        summary = (
            "대화에서 감정 표현이 적거나, 거절·회피 느낌의 표현이 조금 섞여 있을 수 있어요. "
            "너무 조급해하지 말고, 상대의 상황과 컨디션을 배려하면서 천천히 다가가 보세요."
        )

    return {
        "interestScore": int(score),
        "interestLabel": label,
        "topic": topic,      # 한 줄 요약 (API에서 그대로 사용)
        "summary": summary,  # 좀 더 긴 설명
    }


def infer_topic(keywords):
    """
    기존 API/CLI 호환용: 이제는 '사랑의 큐피트' 한 줄 요약을 반환합니다.
    """
    return infer_love_insight(keywords)["topic"]
