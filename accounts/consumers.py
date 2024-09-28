import cv2
import numpy as np
import base64
from channels.generic.websocket import WebsocketConsumer
from .cheat import process_frame 
import json
from django.core.files.base import ContentFile 
import uuid 
from django.apps import apps

class VideoConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_name = None
        self.class_name = None 

    def receive(self, text_data=None, bytes_data=None):
        CheatingEvent = apps.get_model('accounts', 'CheatingEvent')
        try:
            if text_data:
                if not self.student_name:
                    self.student_name = text_data.strip()
                else:
                    self.class_name = text_data.strip() 

            if bytes_data:
                np_arr = np.frombuffer(bytes_data, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    processed_frame, cheat_status = process_frame(img)

                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    encoded_image = base64.b64encode(buffer).decode('utf-8')
                    
                    response = {
                        'image': 'data:image/jpeg;base64,' + encoded_image,
                        'status': cheat_status 
                    }

                    if cheat_status == "cheating" and self.student_name:
                        image_name = f"{uuid.uuid4()}.jpg"
                        image_data = ContentFile(buffer.tobytes(), image_name)

                        CheatingEvent.objects.create(
                            student_name=self.student_name,
                            class_name=self.class_name,
                            cheating_image=image_data
                        )

                    self.send(text_data=json.dumps(response))
                else:
                    self.send(text_data=json.dumps({'error': 'Failed to decode image.'}))
            else:
                self.send(text_data=json.dumps({'error': 'No image data received.'}))

        except Exception as e:
            self.send(text_data=json.dumps({'error': str(e)}))
