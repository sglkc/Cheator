from channels.generic.websocket import WebsocketConsumer, async_to_sync, json

class WebRtcConsumer(WebsocketConsumer):
    my_name: str

    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'type': 'connection',
            'data': {
                'message': 'connected'
            }
        }))

    def disconnect(self):
        async_to_sync(self.channel_layer.send)(
            self.my_name, self.channel_name
        )

    def receive(self, text_data: str):
        text_json = json.loads(text_data)
        event_type = text_json['type']

        if event_type == 'login':
            self.my_name = text_json['data']['name']

            async_to_sync(self.channel_layer.group_add)(
                self.my_name,
                self.channel_name
            )

        elif event_type == 'call':
            name = text_json['data']['name']
            print(self.my_name, "is calling", name);

            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    'type': 'call_received',
                    'data': {
                        'caller': self.my_name,
                        'rtcMessage': text_json['data']['rtcMessage']
                    }
                }
            )

        elif event_type == 'answer_call':
            caller = text_json['data']['caller']

            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    'type': 'call_answered',
                    'data': {
                        'rtcMessage': text_json['data']['rtcMessage']
                    }
                }
            )

        elif event_type == 'ICEcandidate':

            user = text_json['data']['user']

            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    'type': 'ICEcandidate',
                    'data': {
                        'rtcMessage': text_json['data']['rtcMessage']
                    }
                }
            )

    def call_received(self, event):
        print('Call received by ', self.my_name )
        self.send(text_data=json.dumps({
            'type': 'call_received',
            'data': event['data']
        }))

    def call_answered(self, event):
        print(self.my_name, "'s call answered")
        self.send(text_data=json.dumps({
            'type': 'call_answered',
            'data': event['data']
        }))

    def ICEcandidate(self, event):
        self.send(text_data=json.dumps({
            'type': 'ICEcandidate',
            'data': event['data']
        }))
