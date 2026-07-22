from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    """Vista HTML para la página de login (Pantalla 1)"""
    if request.method == 'POST':
        # Simulación de verificación de credenciales
        email = request.POST.get('email')
        # Redirigir a MFA temporalmente
        return redirect('mfa_ui')
        
    return render(request, 'auth/login.html')

def register_view(request):
    """Vista HTML para la página de registro (Pantalla 1)"""
    if request.method == 'POST':
        lopdp = request.POST.get('lopdp')
        iess = request.POST.get('iess')
        
        if not lopdp:
            messages.error(request, "Debe aceptar el consentimiento LOPDP.")
            return render(request, 'auth/register.html')
            
        # Simulación: validación de elegibilidad IESS (KAN-48)
        if iess == "0000000000":
            messages.error(request, "Afiliación IESS inválida o no elegible.")
            return render(request, 'auth/register.html')
            
        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect('login_ui')
        
    return render(request, 'auth/register.html')

def mfa_view(request):
    """Vista HTML para verificación MFA de 6 dígitos"""
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == "123456":
            messages.success(request, "Autenticación correcta. Bienvenido.")
            return redirect('login_ui') # Redirigimos al login simulando éxito por ahora
        else:
            messages.error(request, "Código incorrecto.")
            
    return render(request, 'auth/mfa.html')
