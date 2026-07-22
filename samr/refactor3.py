import os
import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True) + glob.glob('apps/*/templates/**/*.html', recursive=True)

primary_btn = 'bg-brand-600 hover:bg-brand-700 text-white rounded-lg px-4 py-2 font-semibold shadow-samr transition'
secondary_btn = 'bg-white border border-surface-300 text-surface-700 hover:bg-surface-50 rounded-lg px-4 py-2 font-medium transition'
full_w_primary = 'w-full ' + primary_btn

for path in html_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Replace primary button classes
    content = content.replace('bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2 rounded-lg text-sm transition shadow-sm', primary_btn)
    content = content.replace('bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold px-6 py-2.5 rounded-lg shadow-sm transition', primary_btn)
    content = content.replace('bg-surface-900 text-white rounded-lg px-4 py-2 text-sm font-semibold hover:bg-surface-800', primary_btn)
    content = content.replace('w-full bg-brand-600 text-white rounded-lg py-2.5 font-semibold hover:bg-brand-700', full_w_primary)
    content = content.replace('w-full bg-brand-700 text-white rounded-lg py-2.5 font-semibold hover:bg-brand-800 transition', full_w_primary)
    content = content.replace('w-full bg-brand-700 text-white rounded-lg py-2.5 font-semibold hover:bg-brand-800', full_w_primary)

    # <a> buttons replacements
    content = content.replace('bg-indigo-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-indigo-700', primary_btn)
    content = content.replace('bg-brand-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-brand-700', primary_btn)
    content = content.replace('bg-orange-500 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-orange-600', primary_btn)

    # Reemplazar botones de volver/cancelar
    content = content.replace('px-4 py-2.5 text-sm font-medium text-surface-500 hover:text-surface-700 transition', secondary_btn)
    content = content.replace('text-xs font-semibold bg-white border border-surface-300 rounded-lg px-3 py-1.5 hover:bg-surface-50', secondary_btn)
    
    # Back links
    content = content.replace('<a href="{% url \'triaje:lista\' %}" class="text-sm text-surface-400 hover:text-surface-600 hover:underline transition">← Volver a mis solicitudes</a>',
                              f'<a href="{{% url \'triaje:lista\' %}}" class="{secondary_btn} inline-block mb-4">← Volver</a>')
    
    content = content.replace('<a href="{% url \'portal:dashboard\' %}" class="block mt-6 text-sm text-surface-400 hover:underline">← Volver al panel principal</a>',
                              f'<a href="{{% url \'portal:dashboard\' %}}" class="{secondary_btn} inline-block mt-6">← Volver al panel principal</a>')

    content = content.replace('<a href="{% url \'portal:dashboard\' %}" class="block text-sm text-surface-400 hover:underline">← Volver al panel principal</a>',
                              f'<a href="{{% url \'portal:dashboard\' %}}" class="{secondary_btn} inline-block mt-6">← Volver al panel principal</a>')

    content = content.replace('<a href="{% url \'teleconsulta:lista\' %}" class="block mt-6 text-sm text-surface-400 hover:underline">← Volver a mis consultas</a>',
                              f'<a href="{{% url \'teleconsulta:lista\' %}}" class="{secondary_btn} inline-block mt-6">← Volver a mis consultas</a>')
    
    # Standardize titles
    content = re.sub(r'{%\s*block\s+titulo\s*%}(.*?){%\s*endblock\s*%}', r'{% block titulo %}\1 — SAMR{% endblock %}', content)
    # Fix double " — SAMR — SAMR" if it already existed
    content = content.replace(' — SAMR — SAMR{% endblock %}', ' — SAMR{% endblock %}')

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
