from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Link(models.Model):
    short_link = models.CharField(max_length=6, unique=True)
    long_link = models.CharField(max_length=250)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()


class LinkTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
