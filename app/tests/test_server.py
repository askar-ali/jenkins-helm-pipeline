import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import server  # noqa: E402


class RouteTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(server.route("/healthz"), (200, {"status": "ok"}))

    def test_root(self):
        status, body = server.route("/")
        self.assertEqual(status, 200)
        self.assertIn("version", body)

    def test_not_found(self):
        self.assertEqual(server.route("/nope")[0], 404)


class LiveServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        with urllib.request.urlopen(self.base + path) as r:
            return r.status, r.read().decode()

    def test_health_over_http(self):
        status, body = self.get("/healthz")
        self.assertEqual(status, 200)
        self.assertIn("ok", body)

    def test_unknown_path_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/missing")
        self.assertEqual(ctx.exception.code, 404)

    def test_metrics_count_requests(self):
        self.get("/healthz")
        self.get("/healthz")
        _, text = self.get("/metrics")
        self.assertIn("# TYPE http_requests_total counter", text)
        line = next(l for l in text.splitlines() if l.startswith('http_requests_total{path="/healthz",code="200"}'))
        self.assertGreaterEqual(int(line.rsplit(" ", 1)[1]), 2)


if __name__ == "__main__":
    unittest.main()
