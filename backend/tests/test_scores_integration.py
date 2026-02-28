"""Integration tests for score submission and leaderboard."""


def test_submit_score(auth_client):
    client, token = auth_client
    resp = client.post(
        "/scores",
        json={"score": 10, "shots_taken": 5, "shots_made": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["score"] == 10
    assert data["shots_taken"] == 5
    assert data["shots_made"] == 5


def test_submit_score_requires_auth(client):
    resp = client.post("/scores", json={"score": 10, "shots_taken": 5, "shots_made": 5})
    assert resp.status_code == 403


def test_my_scores_returns_history(auth_client):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/scores", json={"score": 6, "shots_taken": 3, "shots_made": 3}, headers=headers)
    client.post("/scores", json={"score": 4, "shots_taken": 4, "shots_made": 2}, headers=headers)
    resp = client.get("/scores/me", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_leaderboard_is_public(client):
    resp = client.get("/scores/leaderboard")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_leaderboard_returns_top10(auth_client):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(15):
        client.post("/scores", json={"score": i, "shots_taken": 5, "shots_made": i % 6}, headers=headers)
    resp = client.get("/scores/leaderboard")
    assert len(resp.json()) <= 10


def test_leaderboard_ordered_by_score_desc(auth_client):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}
    for score in [3, 10, 7]:
        client.post("/scores", json={"score": score, "shots_taken": 5, "shots_made": 3}, headers=headers)
    board = client.get("/scores/leaderboard").json()
    scores = [s["score"] for s in board]
    assert scores == sorted(scores, reverse=True)
