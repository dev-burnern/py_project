// ============================================
// { 1. 리액트 훅 / 스타일 / 차트 라이브러리 불러오는 구간 }
// ============================================

import { useState } from "react";
import "./assets/KakaoLoveanalysis.css";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  LabelList,
  LineChart,
  Line,
} from "recharts";


// ============================================
// { 2. 메인 컴포넌트: KakaoAnalysis }
// ============================================

function KakaoAnalysis() {
  // --------------------------------------------
  // { 2-1. 화면 상태(state)들 선언 }
  // --------------------------------------------

  // { 서버 요청 중인지 표시 (버튼 비활성화/텍스트 변경용) }
  const [loading, setLoading] = useState(false);
  // { 분석 결과 전체(JSON)를 저장할 상태 }
  const [result, setResult] = useState(null);
  // { 에러 메시지 보여줄 때 쓰는 상태 }
  const [error, setError] = useState("");
  // { 사용자가 textarea에 입력한 카톡 원본 텍스트 }
  const [rawText, setRawText] = useState("");


  // --------------------------------------------
  // { 2-2. "호감도 분석하기" 버튼 클릭 시 호출되는 함수 }
  // --------------------------------------------

  const handleAnalyze = async () => {
    // { 아무 텍스트도 없으면 에러 메시지 띄우고 리턴 }
    if (!rawText.trim()) {
      setError("분석할 카톡 대화를 입력해주세요.");
      return;
    }

    // { 로딩 시작, 이전 에러/결과 초기화 }
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // { 백엔드 Bottle 서버의 /api/analyze_text 엔드포인트로 POST 요청 }
      const res = await fetch("/api/analyze_text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: rawText, // { 사용자가 입력한 카톡 텍스트 그대로 전송 }
        }),
      });

      const data = await res.json();

      // { HTTP 상태 코드가 200번대가 아닐 경우 에러 처리 }
      if (!res.ok) {
        setError(data.error || "분석 중 오류가 발생했습니다.");
      } else {
        // { 분석 결과 JSON을 result에 저장 → 아래 JSX에서 사용 }
        setResult(data);
      }
    } catch (e) {
      console.error(e);
      setError("서버에 연결하지 못했습니다.");
    } finally {
      // { 로딩 끝 }
      setLoading(false);
    }
  };


  // ============================================
  // { 3. 차트/리스트에 쓰기 좋은 형식으로 데이터 가공하는 구간 }
  // ============================================

  // ----- 3-1. 참여자별 막대그래프용 데이터 -----
  const participationData =
    result?.participation?.map((p) => ({
      // { recharts에서 x축에 보여줄 이름 }
      name: p.sender,
      // { y값 (대화량) }
      count: p.count,
    })) ?? [];

  // ----- 3-2. 키워드 상위 목록용 데이터 -----
  const keywordData =
    result?.keywords
      // { 혹시 섞여 있을지 모르니 count 기준으로 정렬 }
      ?.slice()
      .sort((a, b) => b.count - a.count)
      .map((k) => ({
        word: k.word,
        count: k.count,
      })) ?? [];

  // { Top 5만 잘라서 뽑기 }
  const top5Keywords = keywordData.slice(0, 5);

  // ----- 3-3. 시간대별 라인차트용 데이터 -----
  const timeData =
    result?.timeDistribution?.map((t) => ({
      hour: t.hour,
      // { x축에 "0시", "1시" 이런 식으로 표시하기 위한 라벨 }
      label: `${t.hour}시`,
      count: t.count,
    })) ?? [];


  // ============================================
  // { 4. 실제 화면에 렌더링 되는 JSX 부분 }
  // ============================================

  return (
    <div className="kakao-wrap">
      <div className="kakao-card">
        {/* ----------------------------------------
            { 4-1. 카톡 상단 헤더 (뒤로가기, 프로필, 방 제목 등) }
           ---------------------------------------- */}
        <div className="kakao-chat-header">
          <div className="kakao-chat-header-left">
            <span className="kakao-chat-icon kakao-chat-icon--back">‹</span>
            <div className="kakao-chat-profile" />
            <div className="kakao-chat-titlebox">
              <div className="kakao-chat-roomname">사랑의 큐피트</div>
              <div className="kakao-chat-status">상대 마음 분석 중…</div>
            </div>
          </div>
          <div className="kakao-chat-header-right">
            <span className="kakao-chat-cupid">💘</span>
          </div>
        </div>

        {/* ----------------------------------------
            { 4-2. 페이지 타이틀 / 설명 영역 }
           ---------------------------------------- */}
        <header className="kakao-title-area">
          <span className="kakao-badge">사랑의 큐피트 💘</span>
          <h1 className="kakao-title">카톡 대화 호감도 분석기</h1>
          <p className="kakao-sub">
            <span className="kakao-highlight">1:1 카톡 대화</span>를 붙여넣고
            상대방의 마음 온도를 살펴봐요.
          </p>
        </header>

        {/* ----------------------------------------
            { 4-3. 카톡 대화 입력 textarea 구역 }
           ---------------------------------------- */}
        <section className="kakao-input-section">
          <label className="kakao-textarea-label">
            카카오톡 대화 내용
            <textarea
              className="kakao-textarea"
              placeholder={`카카오톡 내보내기 텍스트를 그대로 붙여넣어주세요.\n\n예)\n[오후 1:23] 나 : 뭐해?\n[오후 1:24] 상대 : 너 생각 중 😏`}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
            />
          </label>

          <p className="kakao-help">
            * 대화가 길수록(10줄 이상) 호감도 분석이 더 정확해져요.
          </p>
        </section>

        {/* ----------------------------------------
            { 4-4. 분석 실행 버튼 }
           ---------------------------------------- */}
        <button
          className="kakao-button"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? "🔍 마음 읽는 중..." : "✨ 호감도 분석하기"}
        </button>

        {/* { 에러가 있을 때 빨간색 에러 문구 출력 } */}
        {error && <p className="kakao-error">{error}</p>}

        {/* ----------------------------------------
            { 4-5. result가 있을 때만 결과 영역 렌더링 }
           ---------------------------------------- */}
        {result && (
          <div className="kakao-content">
            {/* ============================ */}
            {/* { 4-5-1. 호감도 요약 말풍선 } */}
            {/* ============================ */}
            <div className="kakao-msg-row kakao-msg-row--bot">
              <div className="kakao-msg-avatar">💘</div>
              <div className="kakao-msg-bubble kakao-msg-bubble--bot">
                <div className="kakao-msg-name">사랑의 큐피트</div>
                <div className="kakao-msg-text">
                  <strong>호감도</strong>: {result.interestLabel}
                  <br />
                  사랑 지수{" "}
                  <span className="kakao-highlight">
                    {result.interestScore}
                  </span>
                  /100, 총{" "}
                  <span className="kakao-highlight">
                    {result.totalMessages}
                  </span>
                  개의 메시지를 기준으로 분석했어요.
                </div>
              </div>
            </div>

            {/* ============================ */}
            {/* { 4-5-2. 한 줄 요약 말풍선 } */}
            {/* ============================ */}
            <div className="kakao-msg-row kakao-msg-row--bot">
              {/* { 아바타는 숨김 처리 (버블 정렬용 더미) } */}
              <div className="kakao-msg-avatar kakao-msg-avatar--hidden" />
              <div className="kakao-msg-bubble kakao-msg-bubble--bot kakao-msg-bubble--wide">
                <div className="kakao-msg-name kakao-msg-name--sub">
                  한 줄 요약
                </div>
                <div className="kakao-msg-text">{result.topic}</div>
              </div>
            </div>

            {/* ============================ */}
            {/* { 4-5-3. 자세한 풀이 말풍선 } */}
            {/* ============================ */}
            <div className="kakao-msg-row kakao-msg-row--bot">
              <div className="kakao-msg-avatar kakao-msg-avatar--hidden" />
              <div className="kakao-msg-bubble kakao-msg-bubble--bot kakao-msg-bubble--wide">
                <div className="kakao-msg-name kakao-msg-name--sub">
                  자세한 풀이
                </div>
                <div className="kakao-msg-text">{result.summary}</div>
              </div>
            </div>

            {/* ============================ */}
            {/* { 4-5-4. 참여자별 대화량 리스트 } */}
            {/* ============================ */}
            <h3 className="kakao-section-subtitle">참여자 대화량</h3>
            <ul className="kakao-list">
              {result.participation.map((p) => (
                <li key={p.sender} className="kakao-bubble">
                  {p.sender} {p.count}회 ({p.ratio}%)
                </li>
              ))}
            </ul>

            {/* ============================ */}
            {/* { 4-5-5. 참여자 막대그래프 } */}
            {/* ============================ */}
            <section className="kakao-chart-section">
              <h4 className="kakao-chart-title">참여자별 대화량 (그래프)</h4>
              <div className="kakao-chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={participationData}
                    margin={{ top: 10, right: 16, left: -10, bottom: 24 }}
                  >
                    {/* { 막대 색 그라디언트 정의 } */}
                    <defs>
                      <linearGradient id="partColor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#FF9A9E" />
                        <stop offset="100%" stopColor="#F6416C" />
                      </linearGradient>
                    </defs>

                    <CartesianGrid strokeDasharray="3 3" stroke="#f3d1dc" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Bar dataKey="count" fill="url(#partColor)" radius={6}>
                      <LabelList dataKey="count" position="top" fontSize={11} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* ============================ */}
            {/* { 4-5-6. 키워드 Top 5 리스트 } */}
            {/* ============================ */}
            <h3 className="kakao-section-subtitle">키워드 Top 5</h3>
            <ul className="keyword-list">
              {top5Keywords.map((k, idx) => (
                <li key={k.word} className="keyword-item">
                  <span className="keyword-rank">{idx + 1}</span>
                  <span className="keyword-word">{k.word}</span>
                  <span className="keyword-count">{k.count}회</span>
                </li>
              ))}
            </ul>

            {/* ============================ */}
            {/* { 4-5-7. 시간대 라인차트 영역 } */}
            {/* ============================ */}
            <section className="kakao-chart-section">
              <h4 className="kakao-chart-title">
                대화/답장이 활발한 시간대 분석
              </h4>
              <div className="kakao-chart-box kakao-chart-box--keywords">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={timeData}
                    margin={{ top: 10, right: 16, left: 0, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3d1dc" />
                    <XAxis dataKey="label" />
                    <YAxis allowDecimals={false} />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#FF6B9C"
                      strokeWidth={3}
                      dot={{
                        fill: "#F6416C",
                        stroke: "#fff",
                        strokeWidth: 2,
                        r: 4,
                      }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default KakaoAnalysis;
