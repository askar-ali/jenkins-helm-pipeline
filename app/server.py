"""Tiny HTTP service used as the pipeline's sample workload."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def route(path):
    if path == "/healthz":
        return 200, {"status": "ok"}
    if path == "/":
        return 200, {"service": "sample", "version": "1.0.0"}
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, body = route(self.path)
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
