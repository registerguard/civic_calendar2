# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import localtime
from django.utils.translation import ugettext, ugettext_lazy as _
from django.urls import reverse

import pytz

# Create your models here.
# http://django-scheduler.readthedocs.io/en/latest/settings.html#scheduler-base-classes
# https://github.com/llazzaro/django-scheduler/pull/280

@python_2_unicode_compatible
class Jurisdiction(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Entity(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, max_length=100)
    owner = models.ForeignKey(User, null=True)
    jurisdiction = models.ForeignKey(Jurisdiction)

    def __str__(self):
        return '({0}) {1}'.format(self.jurisdiction.name, self.name)

    class Meta:
        unique_together = (('name', 'owner', 'jurisdiction',),)
        verbose_name_plural = 'entities'


@python_2_unicode_compatible
class Location(models.Model):
    # geolocate on save:
    # http://stackoverflow.com/questions/2755027/geocoding-an-address-on-form-submission
    # ... or geopy?
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return u'({}) {}, {}'.format(self.city, self.name, self.address)

    class Meta:
        unique_together = (('name', 'address', 'city',),)


@python_2_unicode_compatible
class Meeting(models.Model):
    '''
    Abstract class that gets extended by django-scheduler Event model
    '''
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    location = models.ForeignKey(Location)
    agenda = models.TextField(_("Agenda (optional)"), blank=True)
    contact_phone = models.CharField(max_length=64, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.CharField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        time_utc = self.start
        timezone_pt = pytz.timezone('America/Los_Angeles')
        time_local = time_utc.astimezone(timezone_pt)

        return u'({0}) {1}, {2} meeting'.format(self.entity.jurisdiction.name, self.entity.name, time_local.strftime('%A (%Y-%m-%d)'))


    class Meta:
        abstract = True


    def get_absolute_url(self):
        # page 109
        return reverse('meeting-detail', kwargs={'pk': self.pk})

    def meeting_handle(self):
        '''
        This is basically a replacement __str__ for use in templates as we
        can't use __str__ 'cause it gets overridden by child Event class'
        __str__.
        '''

        time_local = localtime(self.start)

        return u'({0}) {1}, {2} meeting'.format(
            self.entity.jurisdiction.name,
            self.entity.name,
            time_local.strftime('%A (%Y-%m-%d %H:%M)')
        )

    def contact_string(self):
        contact_list = [
            getattr(self, 'contact_phone', None),
            getattr(self, 'contact_email', None),
            getattr(self, 'website', None),
        ]
        contact_list = filter(None, contact_list)
        contact_list_len = len(filter(None, contact_list))
        if contact_list_len == 1:
            return u' {0}.'.format(contact_list[0])
        elif contact_list_len == 2:
            return u' {0} or {1}.'.format(*contact_list)
        elif contact_list_len == 3:
            return u' {0}, {1} or {2}.'.format(*contact_list)
        else:
            return u''


@python_2_unicode_compatible
class Profile(models.Model):
    '''
    Adding fields to User model so that we can have a non-username handle
    to use in the URL of the User-based index page. (Otherwise we'd have to use
    the login username in the URL and that wouldn't be good.)

    And using the OneToOneField method so that we don't have to mess with
    changing the AUTH_USER_MODEL in settings for the entire project.
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pretty_name = models.CharField(max_length=256, blank=True)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return '{0}'.format(self.pretty_name)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
