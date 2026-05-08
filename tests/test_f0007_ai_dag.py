import pytest
import os
from fastapi.testclient import TestClient
from task_management.main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_user():
    """Registers a test user and returns an auth header."""
    username = "testuser_ai"
    password = "testpassword"
    
    # Try to register
    client.post("/register", json={"username": username, "password": password})
    
    # Login to get token
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.parametrize("prompt, expected_count, expected_edges", [
    (
        "Run task A, then task B, then task C",
        3,
        [("A", "B"), ("B", "C")]
    ),
    (
        "A then B and C",
        3,
        [("A", "B"), ("A", "C")]
    ),
    (
        "A and B then C",
        3,
        [("A", "C"), ("B", "C")]
    ),
    (
        "T1 then T2 then T3 then T4 then T5",
        5,
        [("T1", "T2"), ("T2", "T3"), ("T3", "T4"), ("T4", "T5")]
    )
])
def test_ai_generate_dag_structure(prompt, expected_count, expected_edges, setup_test_user):
    """
    Verifies the structure of the AI-generated DAG.
    Uses fuzzy matching for task names.
    """
    response = client.post("/api/ai/generate", json={"prompt": prompt}, headers=setup_test_user)
    
    if response.status_code == 404:
        pytest.skip("AI generation endpoint not yet implemented")
    
    if response.status_code == 500:
        if "API_KEY_INVALID" in response.text or "401" in response.text:
             pytest.skip("AI service unavailable due to invalid API Key")
        assert False, f"Server Error: {response.text}"
        
    assert response.status_code == 200
    data = response.json()
    print(f"\nDEBUG: AI output for prompt '{prompt}': {data}")
    
    assert isinstance(data, list)
    assert len(data) == expected_count
    
    # Fuzzy match names to IDs
    name_to_id = {}
    import re
    for task in data:
        name = task["name"].lower()
        matched = False
        ids = set()
        for u, v in expected_edges:
            ids.add(u)
            ids.add(v)
            
        for ident in ids:
            # Match ID as a separate word or at the end of the string
            if re.search(rf"\b{re.escape(ident.lower())}\b", name):
                name_to_id[task["name"]] = ident
                matched = True
                break
        if not matched:
             name_to_id[task["name"]] = task["name"]

    # Build dependency map using matched IDs
    gen_deps = []
    for task in data:
        target_id = name_to_id.get(task["name"], task["name"])
        for dep_name in task.get("dependencies", []):
            source_id = name_to_id.get(dep_name, dep_name)
            gen_deps.append((source_id, target_id))
            
    # Verify edges
    for u, v in expected_edges:
        assert (u, v) in gen_deps or (u.lower(), v.lower()) in [(s.lower(), t.lower()) for s, t in gen_deps]

def test_ai_generate_dag_unauthorized():
    """Verifies that the endpoint requires authentication."""
    response = client.post("/api/ai/generate", json={"prompt": "test"})
    assert response.status_code == 401
