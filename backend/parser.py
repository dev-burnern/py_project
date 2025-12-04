# ============================================
# { 1. 라이브러리 불러오기 구간 }
# ============================================

import re
import pandas as pd


# ============================================
# { 2. 카카오톡 txt 파일을 DataFrame으로 바꾸는 함수 }
# ============================================

def parse_kakao_chat(filepath: str) -> pd.DataFrame:
    """
    카카오톡 텍스트 파일을 읽어 DataFrame으로 변환합니다.
    - 모바일/PC 버전 형식 자동 감지
    - 줄바꿈(엔터)이 포함된 메시지 처리
    - UTF-8 / CP949 인코딩 자동 시도
    """

    rows = []  # { 한 줄 한 줄 파싱한 결과를 딕셔너리로 모아둘 리스트 }

    # ---------------------------------------------------------
    # { 2-1. 정규표현식(Regex) 패턴 정의 부분 }
    # ---------------------------------------------------------

    # { (1) 날짜 변경선 패턴 }
    # 예) "--------------- 2024년 5월 20일 월요일 ---------------"
    # 포맷이 조금씩 달라질 수 있어서, 연/월/일만 일단 뽑도록 설정
    date_line_pat = re.compile(r'^-*\s*(\d{4})년\s(\d{1,2})월\s(\d{1,2})일')

    # { (2) 모바일 메시지 패턴 }
    # 예) [김철수] [오후 3:30] 안녕하세요
    # [이름] [오전/오후/AM/PM 시간] 메시지
    mobile_msg_pat = re.compile(
        r'^\[(.*?)\]\s*\[(오전|오후|AM|PM)\s*(\d{1,2}:\d{2})\]\s*(.*)$'
    )

    # { (3) PC 메시지 패턴 }
    # 예) 2024. 5. 20. 오후 3:30, 김철수 : 안녕하세요
    # 날짜+시간+이름+메시지가 한 줄에 다 들어있는 형식
    pc_msg_pat = re.compile(
        r'^(\d{4})\.\s?(\d{1,2})\.\s?(\d{1,2})\.?\s+'
        r'(오전|오후|AM|PM)\s+(\d{1,2}:\d{2}),\s+(.*?)\s:\s+(.*)$'
    )

    # { 현재 대화 날짜를 저장해둘 변수. 날짜 줄 나오면 여기 갱신함 }
    current_date = "Unknown"

    # { 2-2. 인코딩 후보들. 하나씩 시도해 보면서 읽어보기 }
    encodings = ["utf-8", "utf-8-sig", "cp949"]

    # ---------------------------------------------------------
    # { 2-3. 파일을 여러 인코딩으로 시도하면서 읽는 루프 }
    # ---------------------------------------------------------
    for enc in encodings:
        try:
            rows = []           # { 인코딩 바뀔 때마다 rows 초기화 }
            current_date = "Unknown"

            with open(filepath, "r", encoding=enc) as f:
                lines = f.readlines()

                # { 파일을 줄 단위로 한 줄씩 돌면서 파싱 }
                for line in lines:
                    line = line.strip()

                    # { 공백 줄은 그냥 건너뜀 }
                    if not line:
                        continue

                    # -----------------------------------------
                    # { [A] 날짜 변경선(날짜만 있는 줄) 체크 구간 }
                    # -----------------------------------------
                    m_date = date_line_pat.match(line)
                    if m_date:
                        year, month, day = m_date.groups()
                        # { 2024-05-20 처럼 yyyy-mm-dd 형태로 저장 }
                        current_date = f"{year}-{int(month):02d}-{int(day):02d}"
                        # { 날짜 줄은 메시지가 아니므로 여기서 다음 줄로 넘어감 }
                        continue

                    # -----------------------------------------
                    # { [B] 모바일 메시지 패턴 체크 구간 }
                    # -----------------------------------------
                    m_mobile = mobile_msg_pat.match(line)
                    if m_mobile:
                        name, ampm, time_str, msg = m_mobile.groups()
                        # { 오전/오후 시간 문자열을 24시간제로 변환 }
                        time_24 = convert_time(ampm, time_str)

                        # { rows 리스트에 한 메시지(한 줄) 정보 추가 }
                        rows.append({
                            "date": current_date,  # { 위에서 기억해둔 날짜 사용 }
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue

                    # -----------------------------------------
                    # { [C] PC 메시지 패턴 체크 구간 }
                    # -----------------------------------------
                    m_pc = pc_msg_pat.match(line)
                    if m_pc:
                        y, m, d, ampm, time_str, name, msg = m_pc.groups()
                        # { PC 형식은 줄마다 날짜가 들어오는 경우가 많아서 여기서도 날짜 생성 }
                        date_str = f"{y}-{int(m):02d}-{int(d):02d}"
                        # { current_date도 같이 갱신해 둠 }
                        current_date = date_str
                        time_24 = convert_time(ampm, time_str)

                        rows.append({
                            "date": date_str,
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue

                    # -----------------------------------------
                    # { [D] 멀티라인(여러 줄로 나뉜 메시지) 처리 구간 }
                    # -----------------------------------------
                    # 위의 세 가지 패턴(날짜/모바일/PC) 어느 것도 아니면서,
                    # 이미 rows에 메시지가 있다면,
                    # 이 줄은 "바로 직전 메시지의 다음 줄"로 이어지는 내용이라고 가정.
                    if rows and len(rows) > 0:
                        rows[-1]["message"] += "\n" + line
                        # { 이어 붙였으면 다음 줄로 넘어감 }
                        continue

            # { 여기까지 에러 없이 왔고, rows에 내용이 있다면 성공으로 보고 루프 종료 }
            if len(rows) > 0:
                break

        except UnicodeDecodeError:
            # { 이 인코딩으로는 파일을 못 읽을 때 발생 → 다음 인코딩으로 넘어감 }
            continue
        except Exception as e:
            # { 그 밖의 예외는 그냥 출력만 하고 다음 인코딩 시도 }
            print(f"Error parsing with {enc}: {e}")
            continue

    # ---------------------------------------------------------
    # { 2-4. rows 리스트를 실제 DataFrame으로 변환해서 반환 }
    # ---------------------------------------------------------
    df = pd.DataFrame(rows)
    return df


# ============================================
# { 3. 시간 문자열(오전/오후/AM/PM)을 24시간제로 바꾸는 함수 }
# ============================================

def convert_time(ampm, time_str):
    """
    오전/오후(AM/PM) 12시간제를 24시간제 문자열(HH:MM)로 변환
    """
    # { "3:30" 같은 문자열을 ":" 기준으로 잘라서 시, 분으로 나눔 }
    hour, minute = map(int, time_str.split(":"))

    # { 영어 AM/PM이 들어와도 한국어 오전/오후랑 같게 처리하기 }
    if ampm.upper() == "PM":
        ampm = "오후"
    if ampm.upper() == "AM":
        ampm = "오전"

    # { 오후인데 12시가 아니면 12를 더해서 24시간제로 변경 (예: 오후 3시 → 15시) }
    if ampm == "오후" and hour != 12:
        hour += 12

    # { 오전 12시는 00시로 바꿔야 함 (예: 오전 12:30 → 00:30) }
    if ampm == "오전" and hour == 12:
        hour = 0

    # { HH:MM 형태의 문자열로 다시 만들어서 반환 }
    return f"{hour:02d}:{minute:02d}"
