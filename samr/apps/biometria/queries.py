"""Consultas especializadas de biometria utilizando funciones de TimescaleDB."""
from django.db import connection


def obtener_tendencia_agregada(paciente_id, tipo_signo, intervalo='1 hour'):
    """
    Agrupa y calcula promedios de lecturas biométricas por intervalos de tiempo (time_bucket)
    optimizados mediante TimescaleDB Hypertable.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT time_bucket(%s::interval, l.tomada_en) AS bucket, AVG(l.valor) as promedio, COUNT(*) as cantidad
            FROM biometria_lecturabiometrica l
            JOIN biometria_dispositivoiot d ON l.dispositivo_id = d.id
            WHERE d.paciente_id = %s AND l.tipo_signo = %s
            GROUP BY bucket
            ORDER BY bucket
        """, [intervalo, paciente_id, tipo_signo])
        columnas = [col[0] for col in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
