from django.db import models

from taggit.managers import TaggableManager


class Vector(models.Model):
    name = models.CharField(max_length=100)
    svg = models.FileField()
    tags = TaggableManager()

    def __str__(self):
        return self.name
