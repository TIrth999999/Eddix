import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, FileNode
from django.contrib.auth.models import AnonymousUser

# In-memory user presence tracking (for demo; use cache for production)
room_users = {}

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'
        self.user = self.scope["user"]
        self.username = self.user.username if self.user.is_authenticated else f"Guest-{self.channel_name[-5:]}"

        # Add user to room user list
        users = room_users.setdefault(self.room_code, set())
        users.add(self.username)
        room_users[self.room_code] = users

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # Broadcast updated user list
        await self.broadcast_user_list()

    async def disconnect(self, close_code):
        # Remove user from room user list
        users = room_users.get(self.room_code, set())
        users.discard(self.username)
        if users:
            room_users[self.room_code] = users
        else:
            room_users.pop(self.room_code, None)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Broadcast updated user list
        await self.broadcast_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']

        if message_type == 'file_change':
            file_id = data['file_id']
            content = data['content']
            operation = data.get('operation', {})
            # Save to database on every change
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
        elif message_type == 'chat_message':
            message = data['message']
            username = self.username
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': message,
                    'username': username
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

    async def broadcast_user_list(self):
        # Broadcast the user list to all clients in the room
        users = set(room_users.get(self.room_code, set()))
        # Always include the room creator
        creator_username = await self.get_room_creator_username(self.room_code)
        if creator_username:
            users.add(creator_username)
        # Replace any guest/anon usernames with 'Anonymous'
        display_users = [u if not u.startswith('Guest-') else 'Anonymous' for u in users]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': display_users
            }
        )

    async def user_list_update(self, event):
        # Send the user list to the frontend
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users']
        }))

    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def save_file_content(self, file_id, content):
        try:
            file_node = FileNode.objects.get(id=file_id)
            file_node.content = content
            file_node.save()
        except FileNode.DoesNotExist:
            pass

    @database_sync_to_async
    def get_room_creator_username(self, room_code):
        try:
            room = Room.objects.get(code=room_code)
            if room.creator:
                return room.creator.username
        except Room.DoesNotExist:
            pass
        return None