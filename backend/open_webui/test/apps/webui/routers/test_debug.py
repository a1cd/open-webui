from test.util.abstract_integration_test import AbstractPostgresTest
from test.util.mock_user import mock_webui_user


class TestDebug(AbstractPostgresTest):
    BASE_PATH = "/debug"

    def test_memory_endpoint_admin_access(self):
        """Test that admin users can access the memory endpoint"""
        with mock_webui_user(role="admin"):
            response = self.fast_api_client.get(self.create_url("/memory"))
        assert response.status_code == 200
        data = response.json()
        assert "rss" in data
        assert "vms" in data
        assert "top_memory_objects" in data
        assert isinstance(data["rss"], (int, float))
        assert isinstance(data["vms"], (int, float))
        assert isinstance(data["top_memory_objects"], list)

    def test_memory_endpoint_user_access_denied(self):
        """Test that regular users cannot access the memory endpoint"""
        with mock_webui_user(role="user"):
            response = self.fast_api_client.get(self.create_url("/memory"))
        assert response.status_code == 200
        data = response.json()
        assert data == {"error": "Unauthorized"}

    def test_memory_endpoint_no_auth(self):
        """Test that unauthenticated requests are denied"""
        response = self.fast_api_client.get(self.create_url("/memory"))
        assert response.status_code == 403