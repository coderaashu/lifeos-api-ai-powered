
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

#tests registration
def test_tasks_require_authentication(client):
    response = client.get("/tasks")
    assert response.status_code in (401, 403)

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert "hashed_password" not in response.json()


def test_duplicate_registration(client):
    payload = {"email": "alice@example.com", "password": "SecurePass123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409

#tests login and invalid passwords

def test_login_and_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "SecurePass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]

#test checks nonexistent user

def test_wrong_password_rejected(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "WrongPass123"},
    )
    assert response.status_code == 401

#rate limiting test

def test_login_rate_limit(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            json={"email": "missing@example.com", "password": "WrongPass123"},
        )

    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "WrongPass123"},
    )
    assert response.status_code == 429

#test health endpoint
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

#test readiness
def test_readiness_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "connected"


#add helper to obtain an access token
def register_and_login(client, email):
    password = "SecurePass123"
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["access_token"]



def test_users_only_see_own_tasks(client):
    alice_token = register_and_login(client, "alice@example.com")
    bob_token = register_and_login(client, "bob@example.com")
    client.post(
        "/tasks",
        json={"title": "Alice task", "description": "Private"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    response = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_cannot_access_another_users_task(client):
    alice_token = register_and_login(client, "alice@example.com")
    bob_token = register_and_login(client, "bob@example.com")
    created = client.post(
        "/tasks",
        json={"title": "Alice task", "description": "Private"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    task_id = created.json()["id"]
    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert response.status_code == 404


def test_cannot_update_another_users_task(client):
    alice = register_and_login(client, "alice@example.com")
    bob = register_and_login(client, "bob@example.com")
    created = client.post(
        "/tasks",
        json={"title": "Alice task", "description": "Private"},
        headers={"Authorization": f"Bearer {alice}"},
    )
    task_id = created.json()["id"]
    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Hijacked"},
        headers={"Authorization": f"Bearer {bob}"},
    )
    assert response.status_code == 404



def test_cannot_delete_another_users_task(client):
    alice = register_and_login(client, "alice@example.com")
    bob = register_and_login(client, "bob@example.com")
    created = client.post(
        "/tasks",
        json={"title": "Alice task", "description": "Private"},
        headers={"Authorization": f"Bearer {alice}"},
    )
    task_id = created.json()["id"]
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {bob}"},
    )
    assert response.status_code == 404

