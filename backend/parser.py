import re
import pandas as pd


def parse_kakao_chat(filepath: str) -> pd.DataFrame:
    """
    카카오톡 텍스트 파일을 읽어 DataFrame으로 변환합니다.
    - 모바일/PC 버전 형식 자동 감지
    - 줄바꿈(엔터)이 포함된 메시지 처리
    - UTF-8 / CP949 인코딩 자동 시도
    """
    rows = []

    date_line_pat = re.compile(r'^-*\s*(\d{4})년\s(\d{1,2})월\s(\d{1,2})일')

    mobile_msg_pat = re.compile(
        r'^\[(.*?)\]\s*\[(오전|오후|AM|PM)\s*(\d{1,2}:\d{2})\]\s*(.*)$'
    )

    pc_msg_pat = re.compile(
        r'^(\d{4})\.\s?(\d{1,2})\.\s?(\d{1,2})\.?\s+'
        r'(오전|오후|AM|PM)\s+(\d{1,2}:\d{2}),\s+(.*?)\s:\s+(.*)$'
    )

    current_date = "Unknown"
    encodings = ["utf-8", "utf-8-sig", "cp949"]

    for enc in encodings:
        try:
            rows = []
            current_date = "Unknown"

            with open(filepath, "r", encoding=enc) as f:
                lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    m_date = date_line_pat.match(line)
                    if m_date:
                        year, month, day = m_date.groups()
                        current_date = f"{year}-{int(month):02d}-{int(day):02d}"
                        continue

                    m_mobile = mobile_msg_pat.match(line)
                    if m_mobile:
                        name, ampm, time_str, msg = m_mobile.groups()
                        time_24 = convert_time(ampm, time_str)

                        rows.append({
                            "date": current_date,
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue

                    m_pc = pc_msg_pat.match(line)
                    if m_pc:
                        y, m, d, ampm, time_str, name, msg = m_pc.groups()
                        date_str = f"{y}-{int(m):02d}-{int(d):02d}"
                        current_date = date_str
                        time_24 = convert_time(ampm, time_str)

                        rows.append({
                            "date": date_str,
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue

                    if rows and len(rows) > 0:
                        rows[-1]["message"] += "\n" + line
                        continue

            if len(rows) > 0:
                break

        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error parsing with {enc}: {e}")
            continue

    df = pd.DataFrame(rows)
    return df


def convert_time(ampm, time_str):
    """
    오전/오후(AM/PM) 12시간제를 24시간제 문자열(HH:MM)로 변환
    """
    hour, minute = map(int, time_str.split(":"))

    if ampm.upper() == "PM":
        ampm = "오후"
    if ampm.upper() == "AM":
        ampm = "오전"

    if ampm == "오후" and hour != 12:
        hour += 12

    if ampm == "오전" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"
