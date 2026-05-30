#!/usr/bin/env python3
"""Startup script for Koyeb deployment - provides web auth code input"""
import os, sys, json, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Write config
config = {
    "api_id": 29393668,
    "api_hash": "3415c2367fcdd7281947b7d21276fc3a",
    "phone": "+79001853729",
    "port": 5000,
    "app_name": "HerokuKoyeb"
}
with open("config.json", "w") as f:
    json.dump(config, f, indent=4)

# Simple web server to get auth code
class CodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            html = """<html><body style="background:#1a1a2e;color:#eee;font-family:sans-serif;padding:40px">
<h2>🔐 Heroku Bot Auth</h2>
<form method="POST" action="/code">
<label>Code from Telegram:</label><br>
<input name="code" placeholder="Enter code" style="padding:8px;width:200px"><br><br>
<button type="submit">Submit</button>
</form>
<p>Введи код из Telegram. После этого бот запустится.</p>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == "/ready":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK" if os.path.exists("/tmp/heroku_code.txt") else b"WAIT")
    
    def do_POST(self):
        if self.path == "/code":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            import urllib.parse
            params = urllib.parse.parse_qs(body)
            code = params.get("code", [""])[0]
            if code:
                with open("/tmp/heroku_code.txt", "w") as f:
                    f.write(code.strip())
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body><h2>Code received! Bot starting...</h2></body></html>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No code")

# Start web server in background
server = HTTPServer(("0.0.0.0", 5000), CodeHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
print("🌐 Web UI on port 5000")

# Start bot
os.environ["DOCKER"] = "1"
os.environ["NO_SUDO"] = "1"
sys.argv = ["python3", "-m", "heroku", "--no-web", "--root", "--port", "5000"]

import heroku.main as hm
try:
    heroku = hm.Heroku()
    heroku.main()
except KeyboardInterrupt:
    pass
finally:
    server.shutdown()
