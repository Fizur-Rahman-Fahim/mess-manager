from django.db import migrations


def seed_mess_settings(apps, schema_editor):
    MessSettings = apps.get_model('mess_core', 'MessSettings')
    if not MessSettings.objects.exists():
        MessSettings.objects.create()


def reverse_seed(apps, schema_editor):
    MessSettings = apps.get_model('mess_core', 'MessSettings')
    MessSettings.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mess_core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_mess_settings, reverse_seed),
    ]
