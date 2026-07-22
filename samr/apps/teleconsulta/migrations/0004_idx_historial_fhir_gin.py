from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('teleconsulta', '0003_historialclinico_contenido_fhir'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS idx_historial_fhir_gin ON teleconsulta_historialclinico USING GIN (contenido_fhir);",
            reverse_sql="DROP INDEX IF EXISTS idx_historial_fhir_gin;"
        ),
    ]
