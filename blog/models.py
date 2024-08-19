from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Group


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name='Temat zajęć: ')
    content = models.TextField(verbose_name='Materiały (linki, ciekawostki itp.): ', )
    uploaded_file = models.FileField(null=True, blank=True, upload_to='uploaded_files/',
                                     verbose_name='Dodaj jeden plik o dowolnym formacie lub paczkę w formacie .zip/.rar/.7z/.tar : ')
    visibility = models.BooleanField(verbose_name='Gdy zaznaczone - post będzie publiczny', default=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Grupa nauczycielska')

    # New fields for co-creation
    co_creation_enabled = models.BooleanField(default=False, verbose_name="Włącz współtworzenie")
    co_creation_mode = models.CharField(
        max_length=10,
        choices=[('open', 'Otwarta'), ('closed', 'Zamknięta')],
        default='open',
        verbose_name='Tryb współtworzenia'
    )
    co_creation_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='co_creation_group', verbose_name='Grupa współtworząca')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})