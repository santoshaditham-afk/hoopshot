"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ScoreDashboard from "@/components/ScoreDashboard";

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (!t) {
      router.replace("/");
    } else {
      setToken(t);
    }
  }, [router]);

  function handleLogout() {
    localStorage.removeItem("token");
    router.replace("/");
  }

  if (!token) return null;

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.75rem" }}>🏀 HoopShot Dashboard</h1>
        <button onClick={handleLogout} style={btnStyle}>Logout</button>
      </div>
      <ScoreDashboard token={token} />
    </main>
  );
}

const btnStyle: React.CSSProperties = {
  padding: "0.5rem 1rem",
  background: "#ef4444",
  color: "#fff",
  border: "none",
  borderRadius: 6,
  cursor: "pointer",
  fontSize: "0.9rem",
};
