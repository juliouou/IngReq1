from django.shortcuts import render

def triaje_view(request):
    """Vista HTML para la página principal de Triaje IA (Pantalla 2)"""
    return render(request, 'triaje/chat.html')
