from django.db import models
from users.models import User, Group


class Events(models.Model):
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='events', blank=True)

    class Meta:
        db_table = "tblevents"
