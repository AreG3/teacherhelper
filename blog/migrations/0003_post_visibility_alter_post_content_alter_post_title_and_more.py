from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_uploaded_file_alter_post_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.BooleanField(default=True, verbose_name='Ustaw widoczność posta: '),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(verbose_name='Materiały (linki, ciekawostki itp.): '),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Temat zajęć: '),
        ),
        migrations.AlterField(
            model_name='post',
            name='uploaded_file',
            field=models.FileField(blank=True, null=True, upload_to='uploaded_files/', verbose_name='Dodaj jeden plik o dowolnym formacie lub paczkę w formacie .zip/.rar/.7z/.tar : '),
        ),
    ]
