# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Task, Trademark, Reminder, Profile
# Register your models here.
admin.site.register(Task)
admin.site.register(Trademark)
admin.site.register(Reminder)
admin.site.register(Profile)
