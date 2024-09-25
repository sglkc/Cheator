from django.db import models
from django.utils import timezone

class User(models.Model):
    nama = models.CharField(max_length=100)
    nim = models.CharField(max_length=20, null=True, blank=True)  # Untuk mahasiswa
    nip = models.CharField(max_length=20, null=True, blank=True)  # Untuk dosen
    password = models.CharField(max_length=100)
    kelas = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=10)  # 'mahasiswa' atau 'dosen'
    gender = models.CharField(max_length=10, null=True, blank=True)
    pnaggilan = models.CharField(max_length=10, null=True, blank=True)


class Class(models.Model):
    name = models.CharField(max_length=100)
    meeting_url = models.CharField(max_length=200, blank=True)
    status = models.BooleanField(default=False)  # Status open/close class

    def __str__(self):
        return self.name
    
class CheatDetection(models.Model):
    student_name = models.CharField(max_length=100, null=True, blank=True)
    class_name = models.CharField(max_length=10, null=True, blank=True)
    screenshot = models.ImageField(upload_to='cheat_screenshots/')
    date = models.DateTimeField(auto_now_add=True)  # Menyimpan tanggal secara otomatis

    def __str__(self):
        return f'{self.student_name} - {self.class_name} - {self.date}'