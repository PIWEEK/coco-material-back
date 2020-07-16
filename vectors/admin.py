from django.contrib.admin import widgets
from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from taggit.models import Tag

from vectors.models import Vector


class VectorForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].widget = widgets.FilteredSelectMultiple('Tags', False)
        self.fields['tags'].queryset = Tag.objects.all()

    class Meta:
        model = Vector
        exclude = []


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    form = VectorForm
    fieldsets = (
        ('Main', {'fields': ('name', 'tags',)}),
        ('Vector', {'fields': ('svg', 'svg_image')}),
    )
    list_display = ['name', 'svg_image_thumb', 'tags']
    readonly_fields = ['svg_image', 'svg_image_thumb']
    list_editable = ['tags']
    list_filter = ['tags']
    search_fields = ['name']
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def svg_image(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=250 height=250 />')

    def svg_image_thumb(self, obj):
        return mark_safe(f'<img src="{obj.svg.url}" width=70 height=70 />')
