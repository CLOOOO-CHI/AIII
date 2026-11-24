import http.server, urllib.request, os

TARGET_API = "https://你的真实API域名/v1"  # 例如 https://api.deepseek.com/v1

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_POST(self):
        self.forward()

    def do_GET(self):
        if self.path.startswith("/v1/"):
            self.forward()
        else:
            super().do_GET()

    def forward(self):
        url = TARGET_API + self.path[3:]
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(url, data=body, method=self.command)
        for k in ("Authorization", "Content-Type"):
            if self.headers.get(k):
                req.add_header(k, self.headers[k])
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                while chunk := resp.read(1024):
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

http.server.HTTPServer(("0.0.0.0", 8080), ProxyHandler).serve_forever()
