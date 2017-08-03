# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Jurisdiction, Entity, Location
from schedule.models import Event

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city',)
    list_editable = ('address', 'city',)
    list_filter = ('city',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('meeting_handle', 'start', 'created',)
    list_editable = ('start',)
    list_filter = ('creator__username',)


class EntityAdmin(admin.ModelAdmin):
    # https://stackoverflow.com/questions/43390140/django-disallowedmodeladminlookup-for-lookup-in-admin-list-filter/44665384#44665384
    list_display = ('name', 'owner', 'jurisdiction',)
    list_editable = ('owner', 'jurisdiction',)
    list_filter = ('owner__username',)
    ordering = ('name',)


admin.site.register(Jurisdiction)
admin.site.unregister(Event)
admin.site.register(Event, EventAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Entity, EntityAdmin)
