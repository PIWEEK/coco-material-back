import os

from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver

from colorfield.fields import ColorField
from taggit.managers import TaggableManager


class Vector(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    tags = TaggableManager()
    svg = models.FileField()
    colored_svg = models.FileField(blank=True, null=True)
    stroke_color = ColorField(blank=True, null=True)
    fill_color = ColorField(blank=True, null=True)
    uploaded = models.DateTimeField(auto_now_add=True)

    @property
    def svg_content(self):
        with open(self.svg.path, 'r') as f:
            text = f.read()
            return text

    @property
    def colored_svg_content(self):
        if not self.colored_svg:
            return ""

        with open(self.colored_svg.path, 'r') as f:
            text = f.read()
            return text

    def __str__(self):
        return self.svg.name


class Featured(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    tag = models.CharField(max_length=100)
    order = models.IntegerField()

    @property
    def vectors(self):
        return Vector.objects.filter(tags__name=self.tag).order_by('?')[0:12]

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.tag


@receiver(models.signals.post_delete, sender=Vector)
def auto_delete_svg_on_deletion(sender, instance, **kwargs):
    if instance.svg:
        if os.path.isfile(instance.svg.path):
            default_storage.delete(instance.svg.path)

    if instance.colored_svg:
        if os.path.isfile(instance.colored_svg.path):
            default_storage.delete(instance.colored_svg.path)


@receiver(models.signals.pre_save, sender=Vector)
def auto_delete_file_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_vector = Vector.objects.get(pk=instance.pk)
    except Vector.DoesNotExist:
        return False

    old_svg = old_vector.svg
    new_svg = instance.svg
    if old_svg != new_svg:
        if os.path.isfile(old_svg.path):
            default_storage.delete(old_svg.path)

    old_colored_svg = old_vector.colored_svg
    new_colored_svg = instance.colored_svg
    if old_colored_svg and old_colored_svg != new_colored_svg:
        if os.path.isfile(old_colored_svg.path):
            default_storage.delete(old_colored_svg.path)
