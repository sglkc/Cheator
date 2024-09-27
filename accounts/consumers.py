import cv2
import numpy as np
import base64
from channels.generic.websocket import WebsocketConsumer
from .cheat import process_frame  # Import process_frame dari cheat.py
import json
from django.core.files.base import ContentFile  # Untuk menyimpan gambar ke ImageField
import uuid  # Untuk membuat nama unik pada file gambar
from django.apps import apps

class VideoConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_name = None  # Simpan nama siswa
        self.class_name = None    # Simpan nama kelas

    def receive(self, text_data=None, bytes_data=None):
        # Memuat model CheatingEvent secara dinamis setelah apps sudah siap
        CheatingEvent = apps.get_model('accounts', 'CheatingEvent')
        try:
            if text_data:
                # Simpan studentName atau className tergantung nilai yang diterima
                if not self.student_name:
                    self.student_name = text_data.strip()  # Simpan studentName
                else:
                    self.class_name = text_data.strip() 
            # Cek apakah `bytes_data` diterima
            if bytes_data:
                # Mengonversi data byte ke format numpy array
                np_arr = np.frombuffer(bytes_data, np.uint8)
                
                # Decode array ke dalam format gambar OpenCV
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    # Memproses frame menggunakan fungsi dari cheat.py
                    processed_frame, cheat_status = process_frame(img)  # Tambahkan cheat_status dari proses

                    # Encode frame hasil pemrosesan sebagai base64 untuk dikirim kembali ke client
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    encoded_image = base64.b64encode(buffer).decode('utf-8')
                    
                    # Membuat payload untuk dikirim balik
                    response = {
                        'image': 'data:image/jpeg;base64,' + encoded_image,
                        'status': cheat_status  # Status kecurangan yang dikembalikan dari cheat.py
                    }

                    # Jika statusnya "cheating", simpan ke database
                    if cheat_status == "cheating" and self.student_name:
                        # Decode image back to raw format to save to database
                        image_name = f"{uuid.uuid4()}.jpg"
                        image_data = ContentFile(buffer.tobytes(), image_name)

                        # Simpan event kecurangan ke database
                        CheatingEvent.objects.create(
                            student_name=self.student_name,
                            class_name=self.class_name,
                            cheating_image=image_data  # Simpan image hasil pemrosesan
                        )

                    # Kirim hasil frame dan status ke client sebagai JSON
                    self.send(text_data=json.dumps(response))
                else:
                    # Kirim pesan kesalahan jika gambar tidak valid
                    self.send(text_data=json.dumps({'error': 'Failed to decode image.'}))
            else:
                # Kirim pesan kesalahan jika tidak ada bytes_data
                self.send(text_data=json.dumps({'error': 'No image data received.'}))

        except Exception as e:
            # Penanganan kesalahan umum
            self.send(text_data=json.dumps({'error': str(e)}))
