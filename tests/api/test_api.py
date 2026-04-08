import pytest
import requests


class TestPublicAPI:
    """
    Tests against JSONPlaceholder — a free public REST API.
    Perfect for learning API testing. No credentials needed.
    URL: https://jsonplaceholder.typicode.com
    """

    BASE = "https://jsonplaceholder.typicode.com"

    # ── GET Tests ─────────────────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_all_users(self):
        response = requests.get(f"{self.BASE}/users")
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 10
        print(f"Got {len(users)} users!")

    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_single_user(self):
        response = requests.get(f"{self.BASE}/users/1")
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == 1
        assert "name" in user
        assert "email" in user
        print(f"User: {user['name']} - {user['email']}")

    @pytest.mark.api
    def test_get_user_not_found(self):
        response = requests.get(f"{self.BASE}/users/9999")
        assert response.status_code == 404
        print("404 returned correctly for missing user!")

    @pytest.mark.api
    def test_get_all_posts(self):
        response = requests.get(f"{self.BASE}/posts")
        assert response.status_code == 200
        posts = response.json()
        assert len(posts) == 100
        print(f"Got {len(posts)} posts!")

    @pytest.mark.api
    def test_get_single_post(self):
        response = requests.get(f"{self.BASE}/posts/1")
        assert response.status_code == 200
        post = response.json()
        assert post["id"] == 1
        assert "title" in post
        assert "body" in post
        print(f"Post title: {post['title'][:40]}...")

    # ── POST Tests ────────────────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.api
    def test_create_post(self):
        payload = {
            "title":  "Enterprise Selenium Framework",
            "body":   "This is my test automation post",
            "userId": 1
        }
        response = requests.post(
            f"{self.BASE}/posts",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert "id" in data
        print(f"Created post with id: {data['id']}")

    @pytest.mark.api
    def test_create_user(self):
        from faker import Faker
        fake = Faker()
        payload = {
            "name":     fake.name(),
            "email":    fake.email(),
            "username": fake.user_name(),
        }
        response = requests.post(
            f"{self.BASE}/users",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        print(f"Created user: {data['name']} id={data['id']}")

    # ── PUT Tests ─────────────────────────────────────────────────────────────

    @pytest.mark.api
    def test_update_post(self):
        payload = {
            "id":     1,
            "title":  "Updated Title",
            "body":   "Updated body content",
            "userId": 1
        }
        response = requests.put(
            f"{self.BASE}/posts/1",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        print(f"Updated post: {data['title']}")

    # ── DELETE Tests ──────────────────────────────────────────────────────────

    @pytest.mark.api
    def test_delete_post(self):
        response = requests.delete(f"{self.BASE}/posts/1")
        assert response.status_code == 200
        print("Post deleted successfully!")

    # ── Schema Validation ─────────────────────────────────────────────────────

    @pytest.mark.api
    def test_user_schema(self):
        response = requests.get(f"{self.BASE}/users/1")
        user = response.json()
        required_fields = ["id", "name", "email",
                           "username", "phone", "website"]
        for field in required_fields:
            assert field in user, f"Missing field: {field}"
            print(f"Field '{field}' present: {user[field]}")
        print("Schema validation passed!")

    # ── Data Driven ───────────────────────────────────────────────────────────

    @pytest.mark.api
    @pytest.mark.parametrize("user_id,expected_name", [
        (1, "Leanne Graham"),
        (2, "Ervin Howell"),
        (3, "Clementine Bauch"),
    ])
    def test_specific_users(self, user_id, expected_name):
        response = requests.get(f"{self.BASE}/users/{user_id}")
        assert response.status_code == 200
        user = response.json()
        assert user["name"] == expected_name
        print(f"Verified user {user_id}: {user['name']}")