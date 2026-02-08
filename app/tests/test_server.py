import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from server import route  # noqa: E402


class RouteTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(route("/healthz"), (200, {"status": "ok"}))

    def test_root(self):
        status, body = route("/")
        self.assertEqual(status, 200)
        self.assertIn("version", body)

    def test_not_found(self):
        self.assertEqual(route("/nope")[0], 404)


if __name__ == "__main__":
    unittest.main()
