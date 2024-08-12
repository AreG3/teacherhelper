from django.db import models
from users.models import User, Group
from django.utils import timezone


def get_default_end_time():
    return timezone.now()


class Events(models.Model):
    user_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(default=get_default_end_time)
    all_day = models.BooleanField(default=False)
    groups = models.ManyToManyField('users.Group', related_name='events', blank=True)

    def __str__(self):
        return f"{self.name} (by {self.user_profile.username})"

    class Meta:
        db_table = "tblevents"
