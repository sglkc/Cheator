import cv2
import numpy as np
import base64
from channels.generic.websocket import WebsocketConsumer
from .cheat import process_frame
from .yawn import detect_yawn
import json
from django.core.files.base import ContentFile
import uuid
from django.apps import apps

class VideoConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_name = None
        self.class_name = None
        self.stat = None

    def receive(self, text_data=None, bytes_data=None):
        CheatingEvent = apps.get_model('accounts', 'CheatingEvent')

        try:
            if text_data:
                text_data = text_data.strip()

                if not self.stat:
                    # Paket pertama: mode (online/offline)
                    self.stat = text_data
                elif not self.student_name:
                    # Paket kedua: student_name
                    self.student_name = text_data
                elif not self.class_name:
                    # Paket ketiga: class_name
                    self.class_name = text_data

            if bytes_data:
                # Setelah menerima semua paket, proses gambar
                if self.stat == "online":
                    self.cheating(bytes_data, CheatingEvent)
                elif self.stat == "offline":
                    self.offline(bytes_data, CheatingEvent)

        except Exception as e:
            self.send(text_data=json.dumps({'error': str(e)}))

    def cheating(self, bytes_data, CheatingEvent):
        # Mengubah bytes_data ke format gambar
        np_arr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is not None:
            # Proses frame menggunakan cheat.py
            processed_frame, cheat_status = process_frame(img)

            # Encode gambar hasil pemrosesan
            _, buffer = cv2.imencode('.jpg', processed_frame)
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            response = {
                'image': 'data:image/jpeg;base64,' + encoded_image,
                'status': cheat_status
            }

            # Jika terdeteksi "cheating", simpan ke database
            if cheat_status == "cheating" and self.student_name and self.class_name:
                image_name = f"{uuid.uuid4()}.jpg"
                image_data = ContentFile(buffer.tobytes(), image_name)

                CheatingEvent.objects.create(
                    student_name=self.student_name,
                    class_name=self.class_name,
                    cheating_image=image_data
                )

            # Kirim hasil deteksi ke client
            self.send(text_data=json.dumps(response))
        else:
            self.send(text_data=json.dumps({'error': 'Failed to decode image.'}))

    def offline(self, bytes_data, CheatingEvent):
        # Menerima data dari WebSocket dan mengubahnya ke format numpy array
        np_arr = np.frombuffer(bytes_data, np.uint8)

        # Decode array menjadi gambar menggunakan OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is not None:
            # Proses frame menggunakan fungsi detect_yawn dari yawn.py
            processed_frame, yawn_status = detect_yawn(img)

            # Encode frame hasil pemrosesan ke format base64
            _, buffer = cv2.imencode('.jpg', processed_frame)
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            # Membuat payload untuk dikirim balik ke client
            response = {
                'image': 'data:image/jpeg;base64,' + encoded_image,
                'status': yawn_status
            }

            if yawn_status == "Menguap" and self.student_name and self.class_name:
                image_name = f"{uuid.uuid4()}.jpg"
                image_data = ContentFile(buffer.tobytes(), image_name)

                CheatingEvent.objects.create(
                    student_name=self.student_name,
                    class_name=self.class_name,
                    cheating_image=image_data
                )

            # Kirim hasil frame dan status ke client dalam format JSON
            self.send(text_data=json.dumps(response))
        else:
            # Kirim pesan error jika gambar tidak dapat didecode
            self.send(text_data=json.dumps({'error': 'Failed to decode image.'}))

