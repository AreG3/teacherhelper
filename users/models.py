from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', verbose_name='Avatar')

    def __str__(self):
        return f'Profil: {self.user.username}'


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='custom_groups')  # Zmiana related_name
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')

    def __str__(self):
        return self.name