from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import Room, FileNode, Profile
import json
import os
import zipfile
import tempfile
from pathlib import Path
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def index(request):
    user_rooms = []
    user_credits = None
    if request.user.is_authenticated:
        user_rooms = Room.objects.filter(creator=request.user).order_by('-created_at')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        user_credits = profile.credits
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            if not request.user.is_authenticated:
                return redirect('/login/?next=/')
            room_name = request.POST.get('room_name', 'Unnamed Room')
            user = request.user
            profile, _ = Profile.objects.get_or_create(user=user)
            user_rooms_count = Room.objects.filter(creator=user).count()
            if user_rooms_count >= 3:
                return render(request, 'index.html', {'error': 'You can only have up to 3 rooms.', 'user_rooms': user_rooms, 'user_credits': user_credits})
            if profile.credits <= 0:
                return render(request, 'index.html', {'error': 'You do not have enough credits to create a room.', 'user_rooms': user_rooms, 'user_credits': user_credits})
            room = Room.objects.create(name=room_name, creator=user)
            profile.credits -= 1
            profile.save()
            return redirect('room', room_code=room.code)
        elif action == 'join':
            if request.user.is_authenticated:
                return redirect('/login/?next=/')
            room_code = request.POST.get('room_code')
            try:
                room = Room.objects.get(code=room_code)
                return redirect('room', room_code=room.code)
            except Room.DoesNotExist:
                return render(request, 'index.html', {'error': 'Room not found', 'user_rooms': user_rooms, 'user_credits': user_credits})
    return render(request, 'index.html', {'user_rooms': user_rooms, 'user_credits': user_credits})

@login_required
@require_POST
def delete_room(request, room_code):
    room = get_object_or_404(Room, code=room_code, creator=request.user)
    room.delete()
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # Optionally, refund credit on delete: profile.credits += 1; profile.save()
    return redirect('index')

def room(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    files = FileNode.objects.filter(room=room).select_related('parent').order_by('path')
    return render(request, 'room.html', {'room': room, 'files': files})

@csrf_exempt
def upload_files(request, room_code):
    if request.method == 'POST':
        room = get_object_or_404(Room, code=room_code)
        files = request.FILES.getlist('files')
        
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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        elif form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            error = 'Invalid username or password.'
    return render(request, 'registration/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def api_file_list(request, room_code):
    room = get_object_or_404(Room, code=room_code)
    files = FileNode.objects.filter(room=room).select_related('parent').order_by('path')
    file_list = [
        {
            'id': f.id,
            'name': f.name,
            'path': f.path,
            'is_directory': f.is_directory,
            'parent': f.parent.id if f.parent else None
        }
        for f in files
    ]
    return JsonResponse({'files': file_list})