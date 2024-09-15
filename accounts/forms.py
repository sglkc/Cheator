from django import forms

class LoginForm(forms.Form):
    nim = forms.CharField(label='NIM', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
