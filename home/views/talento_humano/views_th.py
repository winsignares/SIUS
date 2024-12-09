from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Director Talento Humano').exists())
def director_talento_humano(request):
    return render(request, 'templates/talento_humano/director_th.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Secretaria Talento Humano').exists())
def secretaria_talento_humano(request):
    return render(request, 'templates/talento_humano/secretaria_th.html')