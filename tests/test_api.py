import unittest
from fastapi.testclient import TestClient
from backend.app import app

class TestVeriFactSentinelAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("nebius", data)
        self.assertIn("tavily", data)

    def test_models_endpoint(self):
        resp = self.client.get("/api/models")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("active_model", data)
        self.assertGreater(len(data["supported_models"]), 0)

    def test_frontend_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("VeriFact", resp.text)
        self.assertIn("Sentinel", resp.text)

if __name__ == "__main__":
    unittest.main()
