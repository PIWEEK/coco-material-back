import os

from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from taggit.managers import TaggableManager


class Vector(models.Model):
    name = models.CharField(max_length=100)
    svg = models.FileField()
    tags = TaggableManager()

    @property
    def svg_content(self):
        with open(self.svg.path, 'r') as f:
            text = f.read()
            return text

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=Vector)
def auto_delete_svg_on_deletion(sender, instance, **kwargs):
    if instance.svg:
        if os.path.isfile(instance.svg.path):
            default_storage.delete(instance.svg.path)


@receiver(models.signals.pre_save, sender=Vector)
def auto_delete_file_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Vector.objects.get(pk=instance.pk).svg
    except Vector.DoesNotExist:
        return False

    new_file = instance.svg
    if old_file != new_file:
        if os.path.isfile(old_file.path):
            default_storage.delete(old_file.path)
