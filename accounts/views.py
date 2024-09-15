from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User

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
    if request.session.get('is_logged_in') and request.session.get('user_id'):
        user_id = request.session.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            if user.role == 'mahasiswa':
                if request.method == 'POST':
                    if 'change_password' in request.POST:
                        old_password = request.POST.get('old_password')
                        new_password = request.POST.get('new_password')
                        if old_password and new_password:
                            if check_password(old_password, user.password):
                            # Update dengan password baru
                                user.password = make_password(new_password)
                                user.save()
                                messages.success(request, 'Password berhasil diganti')
                            else:
                                messages.error(request, 'Password saat ini salah')
                        else:
                            messages.error(request, 'Salah satu password kosong')
                return render(request, 'home.html', {'user': user})
            else:
                return redirect('login')
        except User.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

def dashboard_view(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    
    if user.role == 'dosen':
        if request.method == 'POST':
            if 'change_password' in request.POST:
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')

                if old_password and new_password:
                    # Verifikasi password lama
                    if check_password(old_password, user.password):
                        # Update dengan password baru
                        user.password = make_password(new_password)
                        user.save()
                        messages.success(request, 'Password berhasil diganti')
                    else:
                        messages.error(request, 'Password saat ini salah')
                else:
                    messages.error(request, 'Salah satu password kosong')
        mahasiswa = User.objects.filter(role='mahasiswa', kelas=user.kelas).values('nim', 'nama')
        return render(request, 'dashboard.html', {'user': user, 'mahasiswa': mahasiswa})
    
    return redirect('login')


def logout_view(request):
    # Hapus informasi sesi pengguna
    request.session.flush()
    messages.success(request, 'Berhasil Logout')
    return redirect('login')

def index_view(request):
    return render(request, 'index.html')