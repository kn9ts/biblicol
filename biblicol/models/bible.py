from django.db import models
from django.utils import timezone
# from django.db import connection


class Bible(models.Model):
    title = models.CharField(max_length=256)
    bookname = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    verse = models.TextField()
    text = models.TextField()
    keywords = models.TextField(null=True)
    quoted = models.CharField(max_length=100)
    title = models.CharField(max_length=100, null=True)
    abbrev = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now,
                                        blank=True, null=True)
    modified_date = models.DateTimeField(default=timezone.now,
                                         blank=True, null=True)

    # def __init__(self):
    #     """This alters the table to accept FULLTEXT string/column searches"""
    #     cursor = connection.cursor()
    #     query = """
    #     ALTER TABLE biblicol_bible ADD FULLTEXT
    #     search(text, keywords, quoted, title)
    #     """
    #     cursor.execute(query)
