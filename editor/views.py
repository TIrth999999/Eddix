from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import Room, FileNode
import json
import os
import zipfile
import tempfile
from pathlib import Path

def index(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            room_name = request.POST.get('room_name', 'Unnamed Room')
            room = Room.objects.create(name=room_name)
            return redirect('room', room_code=room.code)
        elif action == 'join':
            room_code = request.POST.get('room_code')
            try:
                room = Room.objects.get(code=room_code)
                return redirect('room', room_code=room.code)
            except Room.DoesNotExist:
                return render(request, 'index.html', {'error': 'Room not found'})
    return render(request, 'index.html')

def room(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    files = FileNode.objects.filter(room=room).select_related('parent').order_by('path')
    return render(request, 'room.html', {'room': room, 'files': files})

@csrf_exempt
def upload_files(request, room_code):
    if request.method == 'POST':
        room = get_object_or_404(Room, code=room_code)
        files = request.FILES.getlist('files')
        
        # Clear existing files for this room
        FileNode.objects.filter(room=room).delete()
        
        # Track created directories
        created_dirs = {}
        
        for file in files:
            # Handle directory structure from file path
            file_path = file.name.replace('\\', '/')  # Normalize path separators
            path_parts = file_path.split('/')
            
            print(f"Processing file: {file.name}, path_parts: {path_parts}")  # Debug
            
            # Create directory structure
            current_parent = None
            current_path = ""
            
            # Create directories for all parts except the last one (which is the filename)
            for i, part in enumerate(path_parts[:-1]):  # All but the last part (filename)
                if current_path:
                    current_path = f"{current_path}/{part}"
                else:
                    current_path = part
                
                print(f"Creating directory: {current_path}")  # Debug
                
                if current_path not in created_dirs:
                    dir_node, created = FileNode.objects.get_or_create(
                        room=room,
                        path=current_path,
                        defaults={
                            'name': part,
                            'is_directory': True,  # ← This should be True for directories
                            'parent': current_parent
                        }
                    )
                    created_dirs[current_path] = dir_node
                    current_parent = dir_node
                    print(f"Created directory node: {dir_node.name}, is_directory: {dir_node.is_directory}")  # Debug
                else:
                    current_parent = created_dirs[current_path]
            
            # Create file node
            try:
                file_content = file.read().decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                file_content = str(file.read())  # Fallback for binary files
            
            file_node, created = FileNode.objects.update_or_create(
                room=room,
                path=file_path,
                defaults={
                    'name': path_parts[-1],
                    'is_directory': False,  # ← This should be False for files
                    'content': file_content,
                    'parent': current_parent
                }
            )
            print(f"Created file node: {file_node.name}, is_directory: {file_node.is_directory}")  # Debug
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def get_file_content(request, file_id):
    file_node = get_object_or_404(FileNode, id=file_id)
    return JsonResponse({'content': file_node.content})

def download_room(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    files = FileNode.objects.filter(room=room, is_directory=False)
    
    # Create in-memory zip file
    from io import BytesIO
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_node in files:
            # Ensure content is properly encoded
            content = file_node.content.encode('utf-8') if isinstance(file_node.content, str) else file_node.content
            zip_file.writestr(file_node.path, content)
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{room.name}_{room.code}.zip"'
    
    return response