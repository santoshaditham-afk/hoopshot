"use client";
import { useEffect, useState } from "react";
import { getMyScores, getLeaderboard, type Score } from "@/lib/api";

export default function ScoreDashboard({ token }: { token: string }) {
  const [myScores, setMyScores] = useState<Score[]>([]);
  const [leaderboard, setLeaderboard] = useState<Score[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getMyScores(token), getLeaderboard()])
      .then(([mine, board]) => {
        setMyScores(mine);
        setLeaderboard(board);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p style={{ color: "#94a3b8" }}>Loading...</p>;
  if (error) return <p style={{ color: "#f87171" }}>{error}</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      <Section title="Your Recent Games">
        {myScores.length === 0 ? (
          <p style={{ color: "#94a3b8" }}>No games yet. Play on the iOS app!</p>
        ) : (
          <ScoreTable scores={myScores} showUser={false} />
        )}
      </Section>

      <Section title="🏆 Leaderboard (Top 10)">
        {leaderboard.length === 0 ? (
          <p style={{ color: "#94a3b8" }}>No scores yet.</p>
        ) : (
          <ScoreTable scores={leaderboard} showUser />
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: "1.5rem" }}>
      <h2 style={{ margin: "0 0 1rem", fontSize: "1.1rem" }}>{title}</h2>
      {children}
    </div>
  );
}

function ScoreTable({ scores, showUser }: { scores: Score[]; showUser: boolean }) {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
      <thead>
        <tr style={{ color: "#94a3b8", textAlign: "left" }}>
          <th style={thStyle}>#</th>
          {showUser && <th style={thStyle}>Player</th>}
          <th style={thStyle}>Score</th>
          <th style={thStyle}>Made / Taken</th>
          <th style={thStyle}>Date</th>
        </tr>
      </thead>
      <tbody>
        {scores.map((s, i) => (
          <tr key={s.id} style={{ borderTop: "1px solid #334155" }}>
            <td style={tdStyle}>{i + 1}</td>
            {showUser && <td style={tdStyle}>{s.username ?? "—"}</td>}
            <td style={{ ...tdStyle, fontWeight: 700, color: "#f97316" }}>{s.score}</td>
            <td style={tdStyle}>{s.shots_made} / {s.shots_taken}</td>
            <td style={{ ...tdStyle, color: "#64748b" }}>{new Date(s.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const thStyle: React.CSSProperties = { padding: "0.5rem 0.75rem", fontWeight: 500 };
const tdStyle: React.CSSProperties = { padding: "0.75rem" };
