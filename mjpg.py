#!/usr/bin/env python3

from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import io

from PIL import Image, ImageDraw


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        self.img = Image.new('RGB', (320, 240), color='white')
        self.imgDraw = ImageDraw.Draw(self.img)
        self.buf = io.BytesIO()
        super().__init__(*args, **kwargs)
    
    def renderFrame(self):
        self.buf.seek(0)
        self.img.save(self.buf, 'jpeg', quality=80)
        return self.buf.getvalue()

    def getFrame(self):
        timeString = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        r = Image.effect_noise(self.img.size, 16)
        self.img.paste(r)
        self.imgDraw.text((10, 10), timeString, fill=(0, 0, 0))

        return self.renderFrame()

    def sendFrame(self):
        frame = self.getFrame()

        self.wfile.write(b'--frame\r\n')
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', str(len(frame)))
        self.end_headers()
        self.wfile.write(frame)
        self.end_headers()

    def do_GET(self):
        if self.path != '/stream':
            super().do_GET()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()

        while True:
            self.sendFrame()

HTTPServer(('', 8000), Handler).serve_forever()

