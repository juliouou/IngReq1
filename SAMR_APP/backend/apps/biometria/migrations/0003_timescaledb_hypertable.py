from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('biometria', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE biometria_alerta DROP CONSTRAINT IF EXISTS biometria_alerta_lectura_id_e4703677_fk_biometria;
            ALTER TABLE biometria_alerta DROP CONSTRAINT IF EXISTS biometria_alerta_lectura_id_e4703677_fk_biometria_lecturabiometrica_id;
            ALTER TABLE biometria_lecturabiometrica DROP CONSTRAINT IF EXISTS biometria_lecturabiometrica_pkey CASCADE;
            SELECT create_hypertable('biometria_lecturabiometrica', 'tomada_en', if_not_exists => TRUE, migrate_data => TRUE);
            """,
            reverse_sql=""
        ),
    ]
