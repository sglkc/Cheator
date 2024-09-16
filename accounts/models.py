from django.db import models

class User(models.Model):
    nama = models.CharField(max_length=100)
    nim = models.CharField(max_length=20, null=True, blank=True)  # Untuk mahasiswa
    nip = models.CharField(max_length=20, null=True, blank=True)  # Untuk dosen
    password = models.CharField(max_length=100)
    kelas = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=10)  # 'mahasiswa' atau 'dosen'
    gender = models.CharField(max_length=10, null=True, blank=True)

class Class(models.Model):
    name = models.CharField(max_length=100)
    meeting_url = models.CharField(max_length=200, blank=True)
    status = models.BooleanField(default=False)  # Status open/close class

    def __str__(self):
        return self.name