from django.db import models
from django.utils.text import slugify

class Resource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, blank=False, null=False)
    slug = models.SlugField(max_length=500, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    file = models.FileField(upload_to="resources/", blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Resource, self).save(*args, **kwargs)
