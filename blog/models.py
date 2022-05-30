from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name='Temat zajęć: ')
    content = models.TextField(verbose_name='Materiały (linki, ciekawostki itp.): ', )
    uploaded_file = models.FileField(null=True, blank=True, upload_to='uploaded_files/', verbose_name='Dodaj pliki')
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})