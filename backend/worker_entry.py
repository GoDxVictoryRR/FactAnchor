import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"FactAnchor Celery Worker is running!")

def run_dummy_server():
    """
    Render Free Web Services require the application to bind to a specific $PORT 
    within 15 minutes of deployment, otherwise the deployment fails.
    Since Celery is purely a background worker and doesn't explicitly bind to an HTTP port,
    we spawn a lightweight, zero-dependency dummy python HTTP server in a background thread to
    intercept Render's health checks and trick it into keeping our free container alive.
    """
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"[Dummy Server] Listening on port {port} to satisfy Render health checks...")
    server.serve_forever()

if __name__ == "__main__":
    # Start the dummy web server in a background thread
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # Start the Celery worker in the main thread (blocking)
    print("[Celery Wrapper] Booting up Celery background worker...")
    subprocess.run(["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"])
