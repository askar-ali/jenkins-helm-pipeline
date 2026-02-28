"""Tiny HTTP service used as the pipeline's sample workload."""
import json
import os
import signal
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "1.0.0")
REQUESTS = Counter()
LOCK = threading.Lock()


def route(path):
    if path == "/healthz":
        return 200, {"status": "ok"}
    if path == "/":
        return 200, {"service": "sample", "version": VERSION}
    return 404, {"error": "not found"}


def render_metrics():
    """Prometheus text exposition format."""
    lines = ["# HELP http_requests_total Total HTTP requests.", "# TYPE http_requests_total counter"]
    with LOCK:
        for (path, code), n in sorted(REQUESTS.items()):
            lines.append(f'http_requests_total{{path="{path}",code="{code}"}} {n}')
    lines.append(f'app_info{{version="{VERSION}"}} 1')
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            payload, ctype, status = render_metrics().encode(), "text/plain; version=0.0.4", 200
        else:
            status, body = route(self.path)
            payload, ctype = json.dumps(body).encode(), "application/json"
            with LOCK:
                REQUESTS[(self.path if status != 404 else "other", status)] += 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def serve(port=8080):
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)

    def shutdown(*_):
        # Kubernetes sends SIGTERM on rollout; finish in-flight requests, then exit 0.
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    server.serve_forever()
    server.server_close()


if __name__ == "__main__":
    serve(int(os.environ.get("PORT", "8080")))
