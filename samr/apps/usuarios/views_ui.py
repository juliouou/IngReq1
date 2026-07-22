from django.shortcuts import render

def login_view(request):
    """Vista HTML para la página de login (Pantalla 1)"""
    return render(request, 'auth/login.html')

def register_view(request):
    """Vista HTML para la página de registro (Pantalla 1)"""
    return render(request, 'auth/register.html')

def mfa_view(request):
    """Vista HTML para verificación MFA de 6 dígitos"""
    return render(request, 'auth/mfa.html')
