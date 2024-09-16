from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Class

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

    mahasiswa = User.objects.filter(role='mahasiswa', kelas=user.kelas).values('nim', 'nama')
    classes = Class.objects.filter(name=user.kelas)
    return render(request, 'dashboard.html', {'user': user, 'mahasiswa': mahasiswa, 'classes': classes})
    

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
    # Pastikan hanya pengajar yang bisa mengakses fungsi ini
    user_id = request.session.get('user_id')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if user.role == 'dosen':
        # Cari kelas berdasarkan nama kelas dari user dosen
        kelas = get_object_or_404(Class, name=user.kelas)
        
        # Ubah status kelas menjadi 'False' (Close Class)
        kelas.status = False
        kelas.save()
        
        # Berikan feedback ke pengguna
        messages.success(request, f'Kelas {kelas.name} sudah ditutup.')
    else:
        messages.error(request, 'Anda tidak memiliki izin untuk menutup kelas ini.')

    return redirect('dashboard')

def logout_view(request):
    # Hapus informasi sesi pengguna
    request.session.flush()
    messages.success(request, 'Anda sudah Logout')
    return redirect('login')

def join_class_view(request):
    # Ambil user dari sesi
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    # Cari class berdasarkan kelas user
    student_class = Class.objects.filter(name=user.kelas).first()

    if student_class and student_class.status:
        # Arahkan ke URL meeting yang sesuai dengan kelas
        return redirect(f'/class/room/{student_class.meeting_url}')
    else:
        return redirect('home')
    
def index_view(request):
    return render(request, 'index.html')

def class_room_view(request, meeting_url):
    # Tampilkan room berdasarkan URL yang dimasukkan
    return render(request, 'class_room.html', {'meeting_url': meeting_url})