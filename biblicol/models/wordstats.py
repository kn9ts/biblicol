from django.db import models


class WordStats(models.Model):
    word = models.CharField(max_length=100)
    count = models.IntegerField()
