# ============================================
# { 1. 라이브러리 임포트 + Kiwi 준비 + 불용어 설정 구간 }
# ============================================

import pandas as pd
from kiwipiepy import Kiwi   # 한국어 형태소 분석
from sklearn.feature_extraction.text import CountVectorizer  # 단어 빈도 계산용

# { Kiwi 초기화 시도. 안 되면 kiwi = None 으로 두고 콘솔에 에러만 찍음 }
try:
    kiwi = Kiwi()
except Exception as e:
    print("[오류] Kiwi 불러오는 데 문제가 있어요. pip install kiwipiepy 확인해주세요.", e)
    kiwi = None

# { 자주 나오지만 의미는 별로 없는 단어들(불용어). 나중에 키워드 뽑을 때 제외함 }
STOPWORDS = {
    "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "이거", "저거", "그거", "근데",
    "진짜", "너무", "아니", "이제", "오늘", "내일", "그냥",
    "사람", "생각", "좀", "나", "너", "우리", "사진"
}


# ============================================
# { 2. 참여도 분석 함수: 사람별 말한 횟수 / 비율 계산 }
# ============================================

def analyze_participation(df):
    """
    사람별로 몇 번 말했는지랑 비율 계산
    """
    # { df가 비었거나 None이면 그냥 빈 리스트 반환 }
    if df is None or df.empty:
        return []

    # { sender(보낸 사람) 기준으로 메시지가 몇 개씩 있는지 셈 }
    counts = df["sender"].value_counts()
    total = len(df)

    result = []
    # { 각 사람별로 count, 비율(ratio)을 계산해서 딕셔너리로 저장 }
    for sender, cnt in counts.items():
        info = {
            "sender": sender,
            "count": int(cnt),
            "ratio": round(cnt / total * 100, 1)
        }
        result.append(info)

    # { 최종적으로 리스트 형태로 반환 }
    return result


# ============================================
# { 3. 키워드 추출 함수: 명사만 뽑아서 단어 빈도 계산 }
# ============================================

def extract_keywords(df, top_n=20):
    """
    Kiwi로 명사 뽑고 CountVectorizer로 빈도 세서
    상위 키워드 리턴
    """
    # { df가 없거나 비었으면 키워드도 없음 }
    if df is None or df.empty:
        return []
    # { Kiwi를 못 불러온 경우(kiwi is None)에도 키워드 분석 건너뜀 }
    if kiwi is None:
        return []

    # { 메시지 컬럼에서 NaN 제거 후 문자열로 변환 }
    messages_series = df["message"].dropna().astype(str)
    messages = messages_series.tolist()

    if len(messages) == 0:
        return []

    # { Kiwi를 이용해서 한 문장에서 쓸만한 명사만 뽑는 토크나이저 함수 }
    def kiwi_tokenizer(text):
        # text 한 줄을 형태소 분석
        tokens = kiwi.tokenize(text)
        words = []
        for t in tokens:
            # { NNG, NNP(명사)만 사용 + 1글자짜리 제외 + STOPWORDS에 있으면 제외 }
            if t.tag.startswith("NN") and len(t.form) > 1 and t.form not in STOPWORDS:
                words.append(t.form)
        return words

    # { CountVectorizer로 전체 메시지에서 단어 빈도 계산 준비 }
    vectorizer = CountVectorizer(
        tokenizer=kiwi_tokenizer,  # { 위에서 만든 커스텀 토크나이저 사용 }
        max_features=top_n         # { 상위 top_n개 단어만 사용 }
    )

    try:
        # { 메시지 전체에 대해 단어 빈도 행렬 만들기 }
        X = vectorizer.fit_transform(messages)
        feature_names = vectorizer.get_feature_names_out()

        # { 각 단어별 전체 빈도 합 계산 }
        sums = X.sum(axis=0)
        try:
            # { 보통 .A1로 1차원 배열 형태로 가져올 수 있음 }
            word_counts = sums.A1
        except Exception:
            # { 혹시 .A1이 안 되는 경우 리스트로 변환해서 사용 }
            word_counts = sums.tolist()[0]

    except ValueError:
        # { 텍스트가 너무 적거나 분석할 게 없을 때 발생하는 오류 처리 }
        return []
    except Exception as e:
        # { 기타 예외 상황은 로그만 찍고 빈 리스트 반환 }
        print("[키워드 추출 오류]", e)
        return []

    # { 단어와 그 단어의 빈도를 묶어서 리스트로 만들기 }
    keywords = []
    for word, count in zip(feature_names, word_counts):
        keywords.append({
            "word": word,
            "count": int(count)
        })

    # { 빈도수 기준으로 내림차순 정렬 }
    keywords.sort(key=lambda x: x["count"], reverse=True)
    return keywords


# ============================================
# { 4. 시간대별 대화량 분석 함수: 0~23시 기준 메시지 수 }
# ============================================

def analyze_time_distribution(df):
    """
    카톡이 몇 시에 많이 왔다 갔다 했는지 보는 함수 (0~23시)
    실제 '답장 딜레이' 말고, 그냥 메시지 많이 온 시간대 기준
    """
    # { df가 없거나 비어 있으면 빈 리스트 반환 }
    if df is None or df.empty:
        return []

    dt_series = None

    # { datetime 이라는 컬럼이 있으면 그걸 쓰고, 아니면 time 컬럼을 시도 }
    if "datetime" in df.columns:
        dt_series = pd.to_datetime(df["datetime"], errors="coerce")
    elif "time" in df.columns:
        # 시간 형식이 "HH:MM"이라고 가정
        dt_series = pd.to_datetime(df["time"], format="%H:%M", errors="coerce")
    else:
        # { 둘 다 없으면 시간 분석 불가 }
        return []

    # { 변환에 실패한 값은 제거 }
    dt_series = dt_series.dropna()
    if dt_series.empty:
        return []

    # { 각 메시지를 보낸 시(hour)만 뽑아서 개수 세기 }
    counts = dt_series.dt.hour.value_counts().sort_index()

    # { 0~23시까지 전부 채워 넣기. 없는 시간대는 count = 0 지정 }
    result = []
    for hour in range(24):
        cnt = counts.get(hour, 0)
        result.append({
            "hour": int(hour),
            "count": int(cnt)
        })

    return result


# ============================================
# { 5. 사랑/호감도 추론 함수: 키워드 기반 점수 계산 }
# ============================================

def infer_love_insight(keywords):
    """
    키워드 보고 대충 연애/호감 느낌 점수 내기
    (기능은 그대로, 말투만 살짝 가볍게)
    """
    # { 키워드가 하나도 없으면 '데이터 부족' 상태로 리턴 }
    if not keywords:
        return {
            "interestScore": 0,
            "interestLabel": "데이터 부족 😢",
            "topic": "대화량이 너무 적어서 마음을 읽기 어려워요.",
            "summary": "조금 더 대화를 나누고 다시 분석해보는 건 어떨까요?",
        }

    # { 키워드 리스트에서 'word'만 모아서 중복 제거한 집합 만들기 }
    words_set = set()
    for k in keywords:
        word = k.get("word")
        if word:
            words_set.add(word)

    # { 강한 애정/연애 관련 단어들 }
    strong_love_words = {
        "사랑", "사랑해", "좋아해", "너밖에", "보고싶", "보고싶다",
        "보고 싶다", "설레", "썸", "심쿵", "고백", "사귀자", "연애","자기", "자기야", "여보", "여보야"
        "공주","왕자","내꺼","내꺼야","결혼","술","크리스마스"
    }
    # { 가벼운 칭찬/호감/데이트 느낌 단어들 }
    light_love_words = {
        "귀엽", "귀여워", "이쁘다", "예쁘다", "잘생겼", "멋있다",
        "데이트", "영화", "밥먹자", "밥이나", "술한잔", "술 한잔",
        "만날까", "보자", "만나자","연락", "전화", "심심", "보고싶네", "만나",
        "언제", "시간", "약속"
    }
    # { 거절, 피곤, 귀찮음 등 부정적인 분위기 단어들 }
    cold_words = {
        "바빠", "피곤", "나중에", "귀찮", "힘들", "관심없", "됐어",
        "그만", "몰라", "싫어", "안돼"
    }

    # { 각 그룹별로 몇 종류의 단어가 실제로 등장했는지 카운트 }
    strong_hits = 0
    for w in strong_love_words:
        if w in words_set:
            strong_hits += 1

    light_hits = 0
    for w in light_love_words:
        if w in words_set:
            light_hits += 1

    cold_hits = 0
    for w in cold_words:
        if w in words_set:
            cold_hits += 1

    # { 기본 점수 50에서 시작해서, 단어 그룹에 따라 가감점 }
    score = 50
    score += 18 * strong_hits   # { 강한 애정 표현은 점수 크게 올림 }
    score += 10 * light_hits    # { 가벼운 호감/칭찬 단어들 }
    score -= 25 * cold_hits     # { 부정 단어는 점수를 많이 깎음 }

    # { 점수를 0~100 사이로 제한 }
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    # { 점수 구간에 따라 라벨/설명 다르게 설정 }
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
            "서로 눈치를 보는 단계일 수 있고, 이제부터 작은 디테일 하나하나가 관건일 거 같아요!"
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

    # { 점수 + 라벨 + 요약 텍스트까지 모두 묶어서 반환 }
    return {
        "interestScore": int(score),
        "interestLabel": label,
        "topic": topic,
        "summary": summary,
    }


# ============================================
# { 6. 주제 한 줄 요약 함수: 기존 infer_topic 호환용 래퍼 }
# ============================================

def infer_topic(keywords):
    """
    기존 코드 호환용: 한 줄 요약만 따로 뽑기
    """
    # { 위에서 만든 infer_love_insight를 실제로 호출해서 topic만 꺼내 씀 }
    info = infer_love_insight(keywords)
    return info["topic"]
