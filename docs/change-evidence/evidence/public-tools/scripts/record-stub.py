# Records every request body and refuses it, so no model is ever reached.
import http.server, json, sys, os, itertools
out = sys.argv[2]; os.makedirs(out, exist_ok=True); n = itertools.count()
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('content-length', 0)))
        open(f"{out}/{next(n):02d}-{self.path.strip('/').replace('/','_')}.json", 'wb').write(body)
        self.send_response(503); self.send_header('content-type','application/json'); self.end_headers()
        self.wfile.write(b'{"error":{"message":"recording stub: no model behind this endpoint"}}')
    def log_message(self, *a): pass
http.server.HTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
