from django.db import models


class BookStats(models.Model):
    abbrev = models.CharField(max_length=100)
    value = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=256, null=True)
