from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroauditoria',
            name='accion',
            field=models.CharField(max_length=50, verbose_name='Accion'),
        ),
        migrations.AlterField(
            model_name='registroauditoria',
            name='ruta',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Ruta'),
        ),
        migrations.AlterField(
            model_name='registroauditoria',
            name='codigo_estado',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Codigo de estado HTTP'),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='entidad',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Entidad afectada'),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='entidad_id',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='ID de la entidad'),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='estado_anterior',
            field=models.JSONField(blank=True, null=True, verbose_name='Estado anterior'),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='estado_nuevo',
            field=models.JSONField(blank=True, null=True, verbose_name='Estado nuevo'),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='hash_anterior',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='registroauditoria',
            name='hash_actual',
            field=models.CharField(blank=True, default='', editable=False, max_length=64),
        ),
        migrations.AddIndex(
            model_name='registroauditoria',
            index=models.Index(fields=['entidad', 'entidad_id'], name='auditoria_r_entidad_a1b2c3_idx'),
        ),
    ]
