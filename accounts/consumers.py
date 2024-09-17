import cv2
import numpy as np
import base64
from channels.generic.websocket import WebsocketConsumer
from .cheat import process_frame  # Import process_frame dari cheat.py

class VideoConsumer(WebsocketConsumer):
    def receive(self, text_data=None, bytes_data=None):
        # Mengambil frame dari data WebSocket
        np_arr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Memproses frame menggunakan fungsi dari cheat.py
        processed_frame = process_frame(img)

        # Encode hasil pemrosesan untuk dikirim balik ke client
        _, buffer = cv2.imencode('.jpg', processed_frame)
        res = 'data:image/jpg;base64,' + base64.b64encode(buffer).decode()

        # Kirim hasil frame ke client
        self.send(text_data=res)