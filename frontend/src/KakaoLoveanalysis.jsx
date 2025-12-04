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

function KakaoAnalysis() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [rawText, setRawText] = useState("");

  const handleAnalyze = async () => {
    if (!rawText.trim()) {
      setError("분석할 카톡 대화를 입력해주세요.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("/api/analyze_text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: rawText,
        }),
      });

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

  const participationData =
    result?.participation?.map((p) => ({
      name: p.sender,
      count: p.count,
    })) ?? [];

  const keywordData =
    result?.keywords
      ?.slice()
      .sort((a, b) => b.count - a.count)
      .map((k) => ({
        word: k.word,
        count: k.count,
      })) ?? [];

  const top5Keywords = keywordData.slice(0, 5);

  const timeData =
    result?.timeDistribution?.map((t) => ({
      hour: t.hour,
      label: `${t.hour}시`,
      count: t.count,
    })) ?? [];

  return (
    <div className="kakao-wrap">
      <div className="kakao-card">
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

        <header className="kakao-title-area">
          <span className="kakao-badge">사랑의 큐피트 💘</span>
          <h1 className="kakao-title">카톡 대화 호감도 분석기</h1>
          <p className="kakao-sub">
            <span className="kakao-highlight">1:1 카톡 대화</span>를 붙여넣고
            상대방의 마음 온도를 살펴봐요.
          </p>
        </header>

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

        <button
          className="kakao-button"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? "🔍 마음 읽는 중..." : "✨ 호감도 분석하기"}
        </button>

        {error && <p className="kakao-error">{error}</p>}

        {result && (
          <div className="kakao-content">
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

            <div className="kakao-msg-row kakao-msg-row--bot">
              <div className="kakao-msg-avatar kakao-msg-avatar--hidden" />
              <div className="kakao-msg-bubble kakao-msg-bubble--bot kakao-msg-bubble--wide">
                <div className="kakao-msg-name kakao-msg-name--sub">
                  한 줄 요약
                </div>
                <div className="kakao-msg-text">{result.topic}</div>
              </div>
            </div>

            <div className="kakao-msg-row kakao-msg-row--bot">
              <div className="kakao-msg-avatar kakao-msg-avatar--hidden" />
              <div className="kakao-msg-bubble kakao-msg-bubble--bot kakao-msg-bubble--wide">
                <div className="kakao-msg-name kakao-msg-name--sub">
                  자세한 풀이
                </div>
                <div className="kakao-msg-text">{result.summary}</div>
              </div>
            </div>

            <h3 className="kakao-section-subtitle">참여자 대화량</h3>
            <ul className="kakao-list">
              {result.participation.map((p) => (
                <li key={p.sender} className="kakao-bubble">
                  {p.sender} {p.count}회 ({p.ratio}%)
                </li>
              ))}
            </ul>

            <section className="kakao-chart-section">
              <h4 className="kakao-chart-title">참여자별 대화량 (그래프)</h4>
              <div className="kakao-chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={participationData}
                    margin={{ top: 10, right: 16, left: -10, bottom: 24 }}
                  >
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
