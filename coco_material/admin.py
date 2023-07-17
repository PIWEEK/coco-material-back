from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.site_header = "CocoMaterial Admin"
admin.site.site_title = "CocoMaterial Admin"
admin.site.enable_nav_sidebar = False

admin.site.unregister(Group)
