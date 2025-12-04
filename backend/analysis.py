import pandas as pd
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import CountVectorizer

try:
    kiwi = Kiwi()
except Exception as e:
    print("[오류] Kiwi 불러오는 데 문제가 있어요. pip install kiwipiepy 확인해주세요.", e)
    kiwi = None

STOPWORDS = {
    "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "이거", "저거", "그거", "근데",
    "진짜", "너무", "아니", "이제", "오늘", "내일", "그냥",
    "사람", "생각", "좀", "나", "너", "우리", "사진"
}

def analyze_participation(df):
    if df is None or df.empty:
        return []

    counts = df["sender"].value_counts()
    total = len(df)

    result = []
    for sender, cnt in counts.items():
        info = {
            "sender": sender,
            "count": int(cnt),
            "ratio": round(cnt / total * 100, 1)
        }
        result.append(info)

    return result


def extract_keywords(df, top_n=20):
    if df is None or df.empty:
        return []
    if kiwi is None:
        return []

    messages_series = df["message"].dropna().astype(str)
    messages = messages_series.tolist()

    if len(messages) == 0:
        return []

    def kiwi_tokenizer(text):
        tokens = kiwi.tokenize(text)
        words = []
        for t in tokens:
            if t.tag.startswith("NN") and len(t.form) > 1 and t.form not in STOPWORDS:
                words.append(t.form)
        return words

    vectorizer = CountVectorizer(
        tokenizer=kiwi_tokenizer,
        max_features=top_n
    )

    try:
        X = vectorizer.fit_transform(messages)
        feature_names = vectorizer.get_feature_names_out()

        sums = X.sum(axis=0)
        try:
            word_counts = sums.A1
        except Exception:
            word_counts = sums.tolist()[0]

    except ValueError:
        return []
    except Exception as e:
        print("[키워드 추출 오류]", e)
        return []

    keywords = []
    for word, count in zip(feature_names, word_counts):
        keywords.append({
            "word": word,
            "count": int(count)
        })

    keywords.sort(key=lambda x: x["count"], reverse=True)
    return keywords


def analyze_time_distribution(df):
    if df is None or df.empty:
        return []

    dt_series = None

    if "datetime" in df.columns:
        dt_series = pd.to_datetime(df["datetime"], errors="coerce")
    elif "time" in df.columns:
        dt_series = pd.to_datetime(df["time"], format="%H:%M", errors="coerce")
    else:
        return []

    dt_series = dt_series.dropna()
    if dt_series.empty:
        return []

    counts = dt_series.dt.hour.value_counts().sort_index()

    result = []
    for hour in range(24):
        cnt = counts.get(hour, 0)
        result.append({
            "hour": int(hour),
            "count": int(cnt)
        })

    return result


def infer_love_insight(keywords):
    if not keywords:
        return {
            "interestScore": 0,
            "interestLabel": "데이터 부족 😢",
            "topic": "대화량이 너무 적어서 마음을 읽기 어려워요.",
            "summary": "조금 더 대화를 나누고 다시 분석해보는 건 어떨까요?",
        }

    words_set = set()
    for k in keywords:
        word = k.get("word")
        if word:
            words_set.add(word)

    strong_love_words = {
        "사랑", "사랑해", "좋아해", "너밖에", "보고싶", "보고싶다",
        "보고 싶다", "설레", "썸", "심쿵", "고백", "사귀자", "연애","자기", "자기야", "여보", "여보야"
        "공주","왕자","내꺼","내꺼야","결혼","술","크리스마스"
    }
    light_love_words = {
        "귀엽", "귀여워", "이쁘다", "예쁘다", "잘생겼", "멋있다",
        "데이트", "영화", "밥먹자", "밥이나", "술한잔", "술 한잔",
        "만날까", "보자", "만나자","연락", "전화", "심심", "보고싶네", "만나",
        "언제", "시간", "약속"
    }
    cold_words = {
        "바빠", "피곤", "나중에", "귀찮", "힘들", "관심없", "됐어",
        "그만", "몰라", "싫어", "안돼"
    }

    strong_hits = sum(1 for w in strong_love_words if w in words_set)
    light_hits = sum(1 for w in light_love_words if w in words_set)
    cold_hits = sum(1 for w in cold_words if w in words_set)

    score = 50
    score += 18 * strong_hits
    score += 10 * light_hits
    score -= 25 * cold_hits

    if score < 0:
        score = 0
    if score > 100:
        score = 100

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

    return {
        "interestScore": int(score),
        "interestLabel": label,
        "topic": topic,
        "summary": summary,
    }


def infer_topic(keywords):
    info = infer_love_insight(keywords)
    return info["topic"]
