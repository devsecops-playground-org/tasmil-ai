def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["version"]


def test_tools_are_listed(client):
    tools = client.get("/api/tools").json()["tools"]
    assert "swap" in tools
    assert tools == sorted(tools)
