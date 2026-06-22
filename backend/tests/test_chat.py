from app.services.rate_limiter import rate_limiter


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_empty_message(client):
    response = client.post("/chat/message", json={"message": "   "})

    assert response.status_code == 422


def test_creates_session_and_persists_messages(client):
    response = client.post("/chat/message", json={"message": "What is your return policy?"})

    assert response.status_code == 200
    body = response.json()
    assert body["sessionId"]
    assert "30 days" in body["reply"]

    history = client.get(f"/chat/{body['sessionId']}/messages")

    assert history.status_code == 200
    messages = history.json()["messages"]
    assert [message["sender"] for message in messages] == ["user", "ai"]
    assert messages[0]["text"] == "What is your return policy?"


def test_reuses_existing_session(client):
    first = client.post("/chat/message", json={"message": "Do you ship to the USA?"}).json()
    second = client.post(
        "/chat/message",
        json={"sessionId": first["sessionId"], "message": "How long does delivery take?"},
    ).json()

    assert second["sessionId"] == first["sessionId"]

    history = client.get(f"/chat/{first['sessionId']}/messages").json()
    assert len(history["messages"]) == 4


def test_unknown_or_sensitive_message_uses_handoff(client):
    response = client.post("/chat/message", json={"message": "Can you check order number 123?"})

    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["needsHumanHandoff"] is True
    assert "support@northstar.example" in body["reply"]


def test_missing_session_history_returns_404(client):
    response = client.get("/chat/not-a-real-session/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_rate_limit_blocks_abusive_session(client):
    rate_limiter._events.clear()
    first = client.post("/chat/message", json={"message": "What are support hours?"}).json()
    session_id = first["sessionId"]

    blocked = None
    for _ in range(11):
        blocked = client.post("/chat/message", json={"sessionId": session_id, "message": "What are support hours?"})

    assert blocked is not None
    assert blocked.status_code == 429
