import os
import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True) + glob.glob('apps/*/templates/**/*.html', recursive=True)

for path in html_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    
    # 1. Colors replacement
    content = content.replace('teal-', 'brand-')
    content = content.replace('bg-navy', 'bg-surface-900')
    content = content.replace('text-navy', 'text-surface-900')
    content = content.replace('border-navy', 'border-surface-900')
    content = content.replace('slate-', 'surface-')

    # 2. Text replacements
    content = content.replace('RF-01, RF-02, RF-18 — validación de elegibilidad IESS y consentimiento LOPDP incluidos.', 'Proceso seguro con validación de IESS y consentimiento informado.')
    content = content.replace('<p class="text-xs text-surface-400">M2</p>', '')
    content = content.replace('<p class="text-xs text-surface-400">M3</p>', '')
    content = content.replace('<p class="text-xs text-surface-400">M4</p>', '')
    content = content.replace('<p class="text-xs text-surface-400">M5</p>', '')
    content = content.replace('Emitir receta digital · RF-14', 'Emitir receta digital')
    content = content.replace('Simulador IoT (RF-09/10)', 'Simulador de dispositivo IoT')
    content = content.replace('todos los eventos del sistema (RF-20).', 'Historial completo de actividad del sistema.')
    content = content.replace('La API REST completa de los 5 módulos también está disponible en', 'La API REST del sistema está disponible en')

    # Replace primary and secondary button styles where they match old defaults
    # Not using regex here to avoid breaking things, we'll do manual passes for buttons

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
