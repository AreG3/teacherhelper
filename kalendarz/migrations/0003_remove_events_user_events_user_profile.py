from django.db import migrations, models
import django.db.models.deletion


def set_default_user_profile(apps, schema_editor):
    Event = apps.get_model('kalendarz', 'Events')
    Profile = apps.get_model('users', 'Profile')

    # Domyślna wartość dla user_profile, na przykład pierwszy profil w bazie danych
    default_profile = Profile.objects.first()

    Event.objects.filter(user_profile=None).update(user_profile=default_profile)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_profile_image'),
        ('kalendarz', '0002_events_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='user',
        ),
        migrations.AddField(
            model_name='events',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_user_profile),
    ]
