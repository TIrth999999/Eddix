import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, FileNode

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        if message_type == 'file_change':
            file_id = data['file_id']
            content = data['content']
            operation = data.get('operation', {})
            
            # Save to database
            await self.save_file_content(file_id, content)
            
            # Broadcast to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'file_update',
                    'file_id': file_id,
                    'content': content,
                    'operation': operation,
                    'sender': self.channel_name
                }
            )

    async def file_update(self, event):
        if event['sender'] != self.channel_name:  # Don't send back to sender
            await self.send(text_data=json.dumps({
                'type': 'file_update',
                'file_id': event['file_id'],
                'content': event['content'],
                'operation': event.get('operation', {})
            }))

    @database_sync_to_async
    def save_file_content(self, file_id, content):
        try:
            file_node = FileNode.objects.get(id=file_id)
            file_node.content = content
            file_node.save()
        except FileNode.DoesNotExist:
            pass