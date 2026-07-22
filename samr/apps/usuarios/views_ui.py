from django.shortcuts import render

def login_view(request):
    """Vista HTML para la página de login (Pantalla 1)"""
    return render(request, 'auth/login.html')
