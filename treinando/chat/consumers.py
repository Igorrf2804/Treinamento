import json
from channels.generic.websocket import AsyncWebsocketConsumer
from treinando.gemini.models import Coordenador, Aluno

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            recipient_id = self.scope['url_route']['kwargs']['recipient_id']
            recipient = User.objects.get(id=recipient_id)

            if self.user.is_coordinator and not recipient.is_coordinator:
                # Coordenador para aluno
                self.room_group_name = f'coordinator_{self.user.id}_student_{recipient_id}'
            elif not self.user.is_coordinator and recipient.is_coordinator:
                # Aluno para coordenador
                self.room_group_name = f'student_{self.user.id}_coordinator_{recipient_id}'
            else:
                # Outros casos não permitidos
                await self.close()
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
        