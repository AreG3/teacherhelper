# Generated by Django 4.1.6 on 2023-11-30 16:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kalendarz', '0003_remove_events_user_events_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='user_profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
