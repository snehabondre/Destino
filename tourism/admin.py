# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Mobile, Packages, Bookings
from django.contrib import admin

# Register your models here.
admin.site.register(Mobile)
admin.site.register(Packages)
admin.site.register(Bookings)