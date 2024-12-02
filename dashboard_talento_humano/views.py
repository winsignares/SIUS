from django.shortcuts import render

# Create your views here.

def dashboard_talento_humano(request):
    return render(request, 'dashboard_talento_humano.html')