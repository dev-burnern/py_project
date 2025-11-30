// frontend/src/KakaoAnalysis.jsx
import { useState } from "react";
import "./assets/Kakaoanalysis.css";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

function KakaoAnalysis() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/analyze");
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "분석 중 오류가 발생했습니다.");
      } else {
        setResult(data);
      }
    } catch (e) {
      console.error(e);
      setError("서버에 연결하지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // ===== 그래프용 데이터 변환 =====
  const participationData =
    result?.participation?.map((p) => ({
      name: p.sender,
      count: p.count,
    })) ?? [];

  // 키워드는 count 내림차순 정렬해서 사용
  const keywordData =
    result?.keywords
      ?.slice() // 원본 안 건드리려고 복사
      .sort((a, b) => b.count - a.count)
      .map((k) => ({
        word: k.word,
        count: k.count,
      })) ?? [];

  return (
    <div className="kakao-wrap">
      <div className="kakao-card">
        {/* 상단 점 3개 (창 헤더 느낌) */}
        <div className="kakao-header">
          <div className="kakao-dot kakao-dot--red" />
          <div className="kakao-dot kakao-dot--yellow" />
          <div className="kakao-dot kakao-dot--green" />
        </div>

        {/* 타이틀 영역 */}
        <header className="kakao-title-area">
          <span className="kakao-badge">KakaoTalk 분석기</span>
          <h1 className="kakao-title">카카오톡 대화 분석</h1>
          <p className="kakao-sub">
            <span className="kakao-file-tag">assets/chat.txt</span> 파일을 넣고
            분석해봐!
          </p>
        </header>

        {/* 분석 버튼 */}
        <button
          className="kakao-button"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? "🔍 분석 중..." : "✨ 분석하기"}
        </button>

        {error && <p className="kakao-error">{error}</p>}

        {/* ===== 결과 영역 (카드 내부 스크롤) ===== */}
        {result && (
          <div className="kakao-content">
            {/* 요약 텍스트 */}
            <h2 className="kakao-section-title">
              대화 주제:{" "}
              <span className="kakao-highlight">{result.topic}</span>
            </h2>
            <p className="kakao-meta">
              총 메시지 수:{" "}
              <span className="kakao-highlight">
                {result.totalMessages}
              </span>
            </p>

            {/* 참여자 발화량 - 텍스트 리스트 */}
            <h3 className="kakao-section-subtitle">참여자별 발화량</h3>
            <ul className="kakao-list">
              {result.participation.map((p) => (
                <li key={p.sender} className="kakao-bubble">
                  {p.sender} {p.count}회 ({p.ratio}%)
                </li>
              ))}
            </ul>

            {/* 참여자 발화량 - 막대그래프 */}
            <section className="kakao-chart-section">
              <h4 className="kakao-chart-title">참여자별 발화량 (그래프)</h4>
              <div className="kakao-chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={participationData}
                    margin={{ top: 10, right: 16, left: -10, bottom: 24 }}
                  >
                    <defs>
                      {/* 카카오 노랑 그라디언트 */}
                      <linearGradient id="partColor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#FFE76A" />
                        <stop offset="100%" stopColor="#F2C200" />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 11 }}
                      angle={-15}
                      textAnchor="end"
                      interval={0}
                    />
                    <YAxis allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        fontSize: 12,
                        borderRadius: 8,
                        border: "1px solid #eee",
                      }}
                    />
                    <Bar dataKey="count" fill="url(#partColor)" radius={6}>
                      <LabelList
                        dataKey="count"
                        position="top"
                        fontSize={11}
                      />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* 키워드 Top 10 - 텍스트 리스트 */}
            <h3 className="kakao-section-subtitle">핵심 키워드 Top 10</h3>
            <ol className="kakao-list">
              {result.keywords.map((k, idx) => (
                <li
                  key={k.word}
                  className="kakao-bubble kakao-bubble--right"
                >
                  {idx + 1}. {k.word} ({k.count}회)
                </li>
              ))}
            </ol>

            {/* 키워드 빈도 - 막대그래프 (단색 오렌지 + 얇게) */}
            <section className="kakao-chart-section">
              <h4 className="kakao-chart-title">키워드 빈도 (그래프)</h4>
              <div className="kakao-chart-box kakao-chart-box--keywords">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={keywordData}
                    layout="vertical"
                    barSize={18}              // 막대 굵기
                    barGap={6}
                    barCategoryGap="25%"
                    margin={{ top: 10, right: 24, left: 60, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis type="number" allowDecimals={false} />
                    <YAxis
                      type="category"
                      dataKey="word"
                      width={60}              // y축 라벨 폭
                      interval={0}            // 전부 표시
                      tick={{ fontSize: 11 }}
                    />
                    <Tooltip
                      contentStyle={{
                        fontSize: 12,
                        borderRadius: 8,
                        border: "1px solid #eee",
                      }}
                    />
                    <Bar dataKey="count" fill="#FF9F43" radius={6}>
                      <LabelList
                        dataKey="count"
                        position="right"
                        offset={8}           // 숫자와 막대 간격
                        fontSize={11}
                      />
                    </Bar>
                  </BarChart>
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
