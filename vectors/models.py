import os
from xml.dom import minidom

from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Q
from django.db.models.constraints import CheckConstraint
from constrainedfilefield.fields import ConstrainedFileField
from django.dispatch import receiver
from django.utils.functional import cached_property

from colorfield.fields import ColorField
from taggit.managers import TaggableManager


class Vector(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    tags = TaggableManager()
    uploaded = models.DateTimeField(auto_now_add=True)
    search_text = models.TextField(null=True, blank=True)

    # SVG files
    svg = ConstrainedFileField(blank=True, null=True, content_types=['image/svg+xml'])
    colored_svg = ConstrainedFileField(blank=True, null=True, content_types=['image/svg+xml'])
    stroke_color = ColorField(blank=True, null=True)
    fill_color = ColorField(blank=True, null=True)

    # GIF files
    gif = ConstrainedFileField(blank=True, null=True, content_types=['image/gif'])
    colored_gif = ConstrainedFileField(blank=True, null=True, content_types=['image/gif'])

    class Meta:
        ordering = ["id"]
        constraints = [
            CheckConstraint(
                check=(
                    Q(svg__isnull=False) |
                    Q(colored_svg__isnull=False) |
                    Q(gif__isnull=False)  |
                    Q(colored_gif__isnull=False)
                ) ,
                name='vector_should_have_some_file'
            )
        ]

    def __str__(self):
        return self.description

    @cached_property
    def svg_content(self):
        if self.svg:
            try:
                with open(self.svg.path, 'r') as f:
                    text = f.read()
                    return text
            except FileNotFoundError:
                pass

        return ""

    @cached_property
    def colored_svg_content(self):
        if self.colored_svg:
            try:
                with open(self.colored_svg.path, 'r') as f:
                    text = f.read()
                    return text
            except FileNotFoundError:
                pass

        elif self.stroke_color or self.fill_color:
            new_stroke = self.stroke_color or "#000"
            new_fill = self.fill_color  or "#fff"

            try:
                with minidom.parse(self.svg.path) as dom:
                    paths = dom.getElementsByTagName('path')
                    for path in paths:
                        fill = path.getAttribute('fill')
                        if fill in ['#030303', '#000000', '#000', "", None]: # black color
                            fill = f'{new_stroke}'.replace('#none', 'none')
                        else: # fill == fff | ffffff
                            fill = f'{new_fill}'.replace('#none', 'none')
                        path.setAttribute('fill', fill)
                    return dom.toxml()
            except FileNotFoundError:
                pass

        return ""

    def recalculate_search_text(self):
        (Vector.objects
            .filter(id=self.id)
            .update(search_text=" ".join(self.tags.names())))


class Featured(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    tag = models.CharField(max_length=100, blank=True, null=True)
    order = models.IntegerField(default=999)

    @property
    def vectors(self):
        vectors = Vector.objects.all()
        if self.tag:
            vectors = vectors.filter(tags__name=self.tag)
        return vectors.order_by('?')[0:12]

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.tag or ''})"


##################################################################
# SIGNALS
##################################################################

@receiver(models.signals.m2m_changed, sender=Vector.tags.through)
def auto_generate_search_data(sender, instance, action, **kwargs):
    instance.recalculate_search_text()


@receiver(models.signals.post_delete, sender=Vector)
def auto_delete_svg_on_deletion(sender, instance, **kwargs):
    # SVG files
    if instance.svg and os.path.isfile(instance.svg.path):
        default_storage.delete(instance.svg.path)

    if instance.colored_svg and os.path.isfile(instance.colored_svg.path):
        default_storage.delete(instance.colored_svg.path)

    # GIF files
    if instance.gif and os.path.isfile(instance.gif.path):
        default_storage.delete(instance.gif.path)

    if instance.colored_gif and os.path.isfile(instance.colored_gif.path):
        default_storage.delete(instance.colored_gif.path)


@receiver(models.signals.pre_save, sender=Vector)
def auto_delete_file_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_vector = Vector.objects.get(pk=instance.pk)
    except Vector.DoesNotExist:
        return False

    # Svg files
    old_svg = old_vector.svg
    new_svg = instance.svg
    if old_svg and old_svg != new_svg and os.path.isfile(old_svg.path):
        default_storage.delete(old_svg.path)

    old_colored_svg = old_vector.colored_svg
    new_colored_svg = instance.colored_svg
    if old_colored_svg and old_colored_svg != new_colored_svg and os.path.isfile(old_colored_svg.path):
        default_storage.delete(old_colored_svg.path)

    # Gif files
    old_gif = old_vector.gif
    new_gif = instance.gif
    if old_gif and old_gif != new_gif and os.path.isfile(old_gif.path):
        default_storage.delete(old_gif.path)

    old_colored_gif = old_vector.colored_gif
    new_colored_gif = instance.colored_gif
    if old_colored_gif and old_colored_gif != new_colored_gif and os.path.isfile(old_colored_gif.path):
        default_storage.delete(old_colored_gif.path)
