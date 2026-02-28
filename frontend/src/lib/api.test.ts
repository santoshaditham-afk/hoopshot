/**
 * Unit tests for src/lib/api.ts
 * Run with: npm test
 */

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => mockFetch.mockClear());

describe("login()", () => {
  it("returns access token on success", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: "tok123" }),
    });
    const { login } = await import("./api");
    const token = await login("user", "pass");
    expect(token).toBe("tok123");
  });

  it("throws on HTTP error", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Invalid credentials" }),
    });
    const { login } = await import("./api");
    await expect(login("user", "wrong")).rejects.toThrow("Invalid credentials");
  });
});

describe("getLeaderboard()", () => {
  it("returns array of scores", async () => {
    const scores = [{ id: 1, score: 10, shots_taken: 5, shots_made: 5, created_at: "" }];
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => scores });
    const { getLeaderboard } = await import("./api");
    const result = await getLeaderboard();
    expect(result).toEqual(scores);
  });
});

describe("getMyScores()", () => {
  it("sends Bearer token header", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    const { getMyScores } = await import("./api");
    await getMyScores("mytoken");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ headers: { Authorization: "Bearer mytoken" } })
    );
  });
});
