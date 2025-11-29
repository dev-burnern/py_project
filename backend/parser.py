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
    
    # ---------------------------------------------------------
    # 1. 정규표현식 정의 (Regex)
    # ---------------------------------------------------------
    
    # (1) 날짜 변경선 (예: --------------- 2024년 5월 20일 월요일 ---------------)
    # 윈도우/맥/모바일 등 포맷이 조금씩 달라서 유연하게 잡습니다.
    date_line_pat = re.compile(r'^-*\s*(\d{4})년\s(\d{1,2})월\s(\d{1,2})일')

    # (2) 모바일 메시지 패턴 (예: [김철수] [오후 3:30] 안녕하세요)
    mobile_msg_pat = re.compile(r'^\[(.*?)\]\s*\[(오전|오후|AM|PM)\s*(\d{1,2}:\d{2})\]\s*(.*)$')

    # (3) PC 메시지 패턴 (예: 2024. 5. 20. 오후 3:30, 김철수 : 안녕하세요)
    # 날짜 부분이 있거나 없거나, 콤마(,)와 콜론(:) 사이를 잡습니다.
    # PC버전은 메시지 줄마다 날짜가 찍히는 경우가 많습니다.
    pc_msg_pat = re.compile(r'^(\d{4})\.\s?(\d{1,2})\.\s?(\d{1,2})\.?\s+(오전|오후|AM|PM)\s+(\d{1,2}:\d{2}),\s+(.*?)\s:\s+(.*)$')

    current_date = "Unknown" 
    
    # 인코딩 호환성을 위해 여러 방식으로 시도합니다.
    encodings = ["utf-8", "utf-8-sig", "cp949"]
    
    for enc in encodings:
        try:
            rows = [] # 인코딩 바뀔 때마다 초기화
            current_date = "Unknown"
            
            with open(filepath, "r", encoding=enc) as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line: continue

                    # --- [A] 날짜 변경선 체크 ---
                    m_date = date_line_pat.match(line)
                    if m_date:
                        year, month, day = m_date.groups()
                        current_date = f"{year}-{int(month):02d}-{int(day):02d}"
                        continue

                    # --- [B] 모바일 메시지 패턴 체크 ---
                    m_mobile = mobile_msg_pat.match(line)
                    if m_mobile:
                        name, ampm, time_str, msg = m_mobile.groups()
                        time_24 = convert_time(ampm, time_str)
                        
                        rows.append({
                            "date": current_date, # 위에서 저장한 날짜 사용
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue

                    # --- [C] PC 메시지 패턴 체크 ---
                    m_pc = pc_msg_pat.match(line)
                    if m_pc:
                        y, m, d, ampm, time_str, name, msg = m_pc.groups()
                        date_str = f"{y}-{int(m):02d}-{int(d):02d}"
                        current_date = date_str # PC 포맷은 날짜 정보 갱신
                        time_24 = convert_time(ampm, time_str)
                        
                        rows.append({
                            "date": date_str,
                            "time": time_24,
                            "sender": name,
                            "message": msg
                        })
                        continue
                    
                    # --- [D] 멀티라인(줄바꿈) 처리 ---
                    # 위의 패턴들에 해당하지 않는데, 이미 메시지가 존재한다면
                    # 이전 메시지의 내용이 줄바꿈되어 이어지는 것으로 간주합니다.
                    if rows and len(rows) > 0:
                        rows[-1]['message'] += "\n" + line

            # 에러 없이 루프가 끝났으면(파일을 다 읽었으면) 성공으로 간주하고 break
            if len(rows) > 0:
                break 

        except UnicodeDecodeError:
            # 해당 인코딩으로 못 읽으면 다음 인코딩 시도
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
    
    # 영어 표기 통일
    if ampm.upper() == "PM": ampm = "오후"
    if ampm.upper() == "AM": ampm = "오전"

    if ampm == "오후" and hour != 12:
        hour += 12
    if ampm == "오전" and hour == 12:
        hour = 0
        
    return f"{hour:02d}:{minute:02d}"