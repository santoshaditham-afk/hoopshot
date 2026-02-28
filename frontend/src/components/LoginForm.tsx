"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/api";

export default function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"login" | "register">("login");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(username, password);
      }
      const token = await login(username, password);
      localStorage.setItem("token", token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={cardStyle}>
      <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
        <div style={{ fontSize: "3rem" }}>🏀</div>
        <h1 style={{ margin: "0.5rem 0 0", fontSize: "1.5rem" }}>HoopShot</h1>
        <p style={{ margin: "0.25rem 0 0", color: "#94a3b8", fontSize: "0.9rem" }}>Basketball score tracker</p>
      </div>

      <div style={{ display: "flex", marginBottom: "1.5rem", gap: 8 }}>
        {(["login", "register"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            style={{ ...tabStyle, ...(mode === m ? activeTabStyle : {}) }}
          >
            {m === "login" ? "Sign In" : "Register"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />
        {error && <p style={{ color: "#f87171", margin: 0, fontSize: "0.875rem" }}>{error}</p>}
        <button type="submit" disabled={loading} style={submitStyle}>
          {loading ? "..." : mode === "login" ? "Sign In" : "Register & Sign In"}
        </button>
      </form>
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: "#1e293b",
  padding: "2rem",
  borderRadius: 12,
  width: 340,
  boxShadow: "0 4px 24px rgba(0,0,0,0.4)",
};

const inputStyle: React.CSSProperties = {
  padding: "0.75rem 1rem",
  background: "#0f172a",
  border: "1px solid #334155",
  borderRadius: 8,
  color: "#f8fafc",
  fontSize: "1rem",
};

const tabStyle: React.CSSProperties = {
  flex: 1,
  padding: "0.5rem",
  background: "transparent",
  border: "1px solid #334155",
  borderRadius: 6,
  color: "#94a3b8",
  cursor: "pointer",
  fontSize: "0.875rem",
};

const activeTabStyle: React.CSSProperties = {
  background: "#f97316",
  color: "#fff",
  border: "1px solid #f97316",
};

const submitStyle: React.CSSProperties = {
  padding: "0.75rem",
  background: "#f97316",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  fontSize: "1rem",
  cursor: "pointer",
  fontWeight: 600,
};
