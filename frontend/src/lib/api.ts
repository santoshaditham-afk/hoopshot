const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

export async function login(username: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return data.access_token;
}

export async function register(username: string, password: string): Promise<void> {
  await request("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export interface Score {
  id: number;
  score: number;
  shots_taken: number;
  shots_made: number;
  created_at: string;
  username?: string;
}

export async function getMyScores(token: string): Promise<Score[]> {
  return request<Score[]>("/scores/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getLeaderboard(): Promise<Score[]> {
  return request<Score[]>("/scores/leaderboard");
}
