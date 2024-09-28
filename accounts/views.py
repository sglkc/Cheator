import io
import json
import cv2
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import numpy as np
from .models import User, Class,  CheatingEvent
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from. import cheat  # Pastikan file cheat.py diimport
from PIL import Image

@csrf_exempt
def process_frame(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image', '')
        image_data = image_data.split(',')[1]
        image_data = base64.b64decode(image_data)

        image = Image.open(io.BytesIO(image_data))
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        processed_image, cheat_status = cheat.process_frame(image)

        _, buffer = cv2.imencode('.jpg', processed_image)
        encoded_image = base64.b64encode(buffer).decode()

        return JsonResponse({
            'image': 'data:image/jpeg;base64,' + encoded_image,
            'status': cheat_status
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def login_view(request):
    if request.method == 'POST':
        if 'nim' in request.POST:  # Formulir mahasiswa
            nim = request.POST.get('nim')
            password = request.POST.get('password')

            try:
                user = User.objects.get(nim=nim, role='mahasiswa')
                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    request.session['is_logged_in'] = True
                    return redirect('home')
                else:
                    messages.error(request, 'Password salah')
            except User.DoesNotExist:
                messages.error(request, 'NIM tidak terdaftar')

        elif 'nip' in request.POST:  # Formulir dosen
            nip = request.POST.get('nip')
            password = request.POST.get('password')

            try:
                user = User.objects.get(nip=nip, role='dosen')
                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    request.session['is_logged_in'] = True
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Password salah')
            except User.DoesNotExist:
                messages.error(request, 'NIP tidak terdaftar')

    return render(request, 'login.html')


def home_view(request):
    if not request.session.get('is_logged_in') or not request.session.get('user_id'):
        return redirect('login')
    
    user_id = request.session.get('user_id')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
    
    student_class = Class.objects.filter(name=user.kelas).first()

    if user.role != 'mahasiswa':
        return redirect('login')
    
    if request.method == 'POST':
        if 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if not old_password or not new_password:
                messages.error(request, 'Salah satu password kosong')
            elif check_password(old_password, user.password):
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password berhasil diganti')
            else:
                messages.error(request, 'Password saat ini salah')

    context = {
        'user': user,
        'meeting_url': student_class.meeting_url if student_class and student_class.status else None,
        'error': 'Class is not open yet' if student_class and not student_class.status else None
    }
    return render(request, 'home.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import User, Class, CheatingEvent

def dashboard_view(request):
    if not request.session.get('is_logged_in') or not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if user.role != 'dosen':
        return redirect('login')

    if request.method == 'POST':
        if 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if not old_password or not new_password:
                messages.error(request, 'Salah satu password kosong')
            elif check_password(old_password, user.password):
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password berhasil diganti')
            else:
                messages.error(request, 'Password saat ini salah')

    # Retrieve mahasiswa based on the kelas of the logged-in user
    mahasiswa = User.objects.filter(role='mahasiswa', kelas=user.kelas).values('nim', 'nama', 'pnaggilan', 'gender')

    # Retrieve CheatingEvents related to the mahasiswa
    cheating_events = CheatingEvent.objects.filter(student_name__in=[mhs['pnaggilan'] for mhs in mahasiswa])

    # Create a dictionary to store images for each mahasiswa
    cheating_dict = {}
    for event in cheating_events:
        if event.student_name not in cheating_dict:
            cheating_dict[event.student_name] = []
        cheating_dict[event.student_name].append(event.cheating_image.url)

    # Add cheating images URLs to mahasiswa data
    for mhs in mahasiswa:
        mhs['cheating_image_urls'] = ','.join(cheating_dict.get(mhs['pnaggilan'], []))

    classes = Class.objects.filter(name=user.kelas)
    
    return render(request, 'dashboard.html', {
        'user': user,
        'mahasiswa_list': mahasiswa,
        'classes': classes,
        'cheating_dict': cheating_dict,  # Optional: if you need it for other purposes
    })

def open_class_view(request, class_id):
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
    
    if user.role == 'dosen':
        kelas = get_object_or_404(Class, id=class_id)
        kelas.status = True
        kelas.save()
        messages.success(request, f'Kelas {kelas.name} sudah dibuka.')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menutup kelas ini.')
    return redirect('dashboard')

def close_class_view(request):
    user_id = request.session.get('user_id')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if user.role == 'dosen':
        kelas = get_object_or_404(Class, name=user.kelas)
        kelas.status = False
        kelas.save()
        messages.success(request, f'Kelas {kelas.name} sudah ditutup.')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menutup kelas ini.')

    return redirect('dashboard')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Anda sudah Logout')
    return redirect('login')

def join_class_view(request):
    if not request.session.get('is_logged_in') or not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    student_class = Class.objects.filter(name=user.kelas).first()

    if student_class and student_class.status:
        # Simpan informasi pengguna dalam sesi
        request.session['student_name'] = user.pnaggilan
        request.session['class_name'] = user.kelas
        print(f"Student Name: {request.session['student_name']}, Class Name: {request.session['class_name']}")
        return redirect(f'/class/room/{student_class.meeting_url}')
    else:
        return redirect('home')

    
def class_room_view(request, meeting_url):
    if not request.session.get('is_logged_in') or not request.session.get('user_id'):
        return redirect('login')

    # Ambil user dari sesi
    student_name = request.session.get('student_name')
    class_name = request.session.get('class_name')

    # Temukan kelas berdasarkan meeting_url
    student_class = Class.objects.filter(meeting_url=meeting_url).first()

    if student_class:
        context = {
            'student_name': student_name,
            'class_name': class_name,
            'class': student_class,
        }
        return render(request, 'class_room.html', context)
    else:
        return redirect('home')


    
def index_view(request):
    return render(request, 'index.html')

def video_feed_view(request):
    return render(request, 'web.html')
