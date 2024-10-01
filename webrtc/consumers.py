from logging import error
from channels.generic.websocket import WebsocketConsumer, async_to_sync, json
import cv2, base64
import numpy as np

connected_classes = {}

class WebRtcConsumer(WebsocketConsumer):
    supervisor: str       # sebagai nama grup (1 pengawas banyak kelas)
    class_name: str       # sebagai nama channel

    # hapus kelas dari grup pengawas jika disconnect
    def disconnect(self, _):
        if not self.class_name: return

        if self.supervisor in connected_classes:
            connected_classes[self.supervisor].remove(self.class_name)

        async_to_sync(self.channel_layer.group_send)(
            self.supervisor,
            {
                'type': 'class_leave',
                'class_name': self.class_name,
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.supervisor,
            self.class_name
        )

    def receive(self, text_data=None, bytes_data=None):

        # text data buat events
        if text_data:

            # parsing json
            try:
                text_json = json.loads(text_data)
                event_type = text_json['type']
            except:
                error('data ws bukan json')
                return

            # jika kelas baru masuk, set kelas, cari pengawas kelas, dan kirim event
            if event_type == 'class_join':
                self.supervisor = 'Seya' # TODO: contoh nama peungawas ganti dari db
                self.class_name = text_json['class_name']

                # tambah kelas ke koneksi pengawas
                if not self.supervisor in connected_classes:
                    connected_classes[self.supervisor] = []

                connected_classes[self.supervisor].append(self.class_name)

                # kirim event classroom join ke teacher
                async_to_sync(self.channel_layer.group_send)(
                    self.supervisor,
                    {
                        'type': 'class_join',
                        'class_name': self.class_name,
                    }
                )

            # jika pengawas baru masuk, masukkan ke grupnya, dan kirim sukses
            elif event_type == 'supervisor_join':
                self.supervisor = text_json['supervisor']

                async_to_sync(self.channel_layer.group_add)(
                    self.supervisor,
                    self.channel_name
                )

                if self.supervisor in connected_classes:
                    for class_name in connected_classes[self.supervisor]:
                        self.send(json.dumps({
                            'type': 'class_join',
                            'class_name': class_name,
                        }))

                self.send(json.dumps({
                    'type': 'message',
                    'message': 'success'
                }))

        # bytes data buat foto, selalu foto, kirim ke pengawas dan kirim lagi
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.supervisor,
                {
                    'type': 'class_image',
                    'class_name': self.class_name,
                    'image': bytes_data
                }
            )

            self.send(json.dumps({
                'type': 'class_image',
                'data': 'success'
            }))

    # lapor ke pengawas jika ada kelas yang masuk
    def class_join(self, event: dict[str, str]):
        self.send(json.dumps({
            'type': 'class_join',
            'class_name': event['class_name']
        }))

    # lapor ke pengawas jika ada kelas yang masuk
    def class_leave(self, event: dict[str, str]):
        self.send(json.dumps({
            'type': 'class_leave',
            'class_name': event['class_name']
        }))

    def class_image(self, event: dict):
        np_arr = np.frombuffer(event['image'], np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            self.send(json.dumps({
                'image': '',
                'status': False
            }))

            return

        processed_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Encode frame hasil pemrosesan ke format base64
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_image = base64.b64encode(buffer.data).decode('utf-8')

        self.send(json.dumps({
            'type': 'class_image',
            'class_name': event['class_name'],
            'image': 'data:image/jpeg;base64,' + encoded_image,
            'status': True
        }))
