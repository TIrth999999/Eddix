from django.db import models
import uuid
import json
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=10)

    def __str__(self):
        return f"Profile of {self.user.username} (Credits: {self.credits})"

class Room(models.Model):
    code = models.CharField(max_length=10, unique=True, default=str(uuid.uuid4())[:8])
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)    
    def __str__(self):
        return f"Room {self.code} - {self.name} (by {self.creator.username})"

class FileNode(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    path = models.TextField()
    is_directory = models.BooleanField(default=False)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['room', 'path']
    
    def __str__(self):
        return f"{self.room.code}/{self.path}"