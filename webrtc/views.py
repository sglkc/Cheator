from django.shortcuts import render

# Create your views here.
def classroom(request):
    return render(request, 'rtc_classroom.html')

def supervisor(request):
    return render(request, 'rtc_supervisor.html')
