import socket
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
    probe.connect(("192.0.2.1", 9))
    ip = probe.getsockname()[0]
base = f"http://{ip}:8317"
download_url = base + "/VCSReader.3dsx"
qr = QRCode(None,QRErrorCorrectLevel.M)
qr.addData(download_url)
qr.make()
n = qr.getModuleCount()
img = Image.new("RGB",((n+8)*8,)*2,"white")
draw = ImageDraw.Draw(img)
for y in range(n):
    for x in range(n):
        if qr.isDark(y,x):
            a,b=(x+4)*8,(y+4)*8
            draw.rectangle((a,b,a+7,b+7),fill="black")
img.save(root/"Install-QR.png")
files = {"/VCSReader.3dsx":(root/"VCSReader.3dsx").read_bytes()}
class Downloads(BaseHTTPRequestHandler):
    def do_GET(self):
        data=files.get(self.path)
        if data is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Content-Type","application/octet-stream")
        self.send_header('Content-Disposition', 'attachment; filename=VCSReader.3dsx')
        self.end_headers()
        self.wfile.write(data)
if __name__=="__main__":
    with ThreadingHTTPServer((ip,8317),Downloads) as server:
        if "--check" in sys.argv:
            from threading import Thread
            from urllib.request import build_opener, ProxyHandler
            Thread(target=server.serve_forever,daemon=True).start()
            client=build_opener(ProxyHandler({}))
            for path, expected in files.items():
                assert client.open(base+path,timeout=4).read()==expected
            server.shutdown()
            print("Verified direct download", download_url)
        else:
            print("Scan the direct download QR code. Keep this window open.", flush=True)
            if "--headless" not in sys.argv:
                webbrowser.open((root/"Install-QR.png").as_uri())
            server.serve_forever()


