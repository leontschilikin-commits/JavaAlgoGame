# Lokaler Testserver mit Range-Unterstützung (die braucht CheerpJ zum Laden der .jar-Dateien)
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class H(SimpleHTTPRequestHandler):
    def send_head(self):
        rng = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        a = int(rng.group(1)); b = min(int(rng.group(2)) if rng.group(2) else size - 1, size - 1)
        f = open(path, "rb"); f.seek(a)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (a, b, size))
        self.send_header("Content-Length", str(b - a + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self.wfile.write(f.read(b - a + 1)); f.close()
        return None
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes"); self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, *a): pass

os.chdir(sys.argv[2] if len(sys.argv) > 2 else ".")
ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
