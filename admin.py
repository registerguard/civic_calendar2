# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import BaseModelFormSet

from .models import Jurisdiction, Entity, Location, Profile
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
    list_display = ('name', 'owner', 'jurisdiction', 'slug',)
    list_editable = ('owner', 'jurisdiction', 'slug',)
    list_filter = ('owner__username',)
    ordering = ('name',)
    prepopulated_fields = {'slug': ('jurisdiction', 'name',)}


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name= 'user'
    prepopulated_fields = {'slug': ('pretty_name',)}


class CustomeUserAdmin(UserAdmin):
    list_display = ('username', 'profile_pretty_name', 'email', 'first_name', 'last_name', 'is_staff',)
    list_editable = ('first_name', 'last_name',)
    inlines = (ProfileInline,)

    def profile_pretty_name(self, obj):
        return '{0}'.format(obj.profile.pretty_name)
    profile_pretty_name.short_description = 'Pretty name'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomeUserAdmin, self).get_inline_instances(request, obj)


class JurisdictionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Jurisdiction, JurisdictionAdmin)
admin.site.unregister(Event)
admin.site.register(Event, EventAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomeUserAdmin)
