# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

# Create your models here.
# http://django-scheduler.readthedocs.io/en/latest/settings.html#scheduler-base-classes
# https://github.com/llazzaro/django-scheduler/pull/280

@python_2_unicode_compatible
class Jurisdiction(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Entity(models.Model):
    name = models.CharField(max_length=255)
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
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    location = models.ForeignKey(Location)
    agenda = models.TextField(_("Agenda (optional)"), blank=True)
    contact_phone = models.CharField(max_length=64, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.CharField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        # convert db UTC time to PT for presentation
        time_utc = self.start
        timezone_pt = pytz.timezone('America/Los_Angeles')
        time_local = time_utc.astimezone(timezone_pt)

        return u'({0}) {1}, {2} meeting'.format(self.entity.jurisdiction.name, self.entity.name, time_local.strftime('%A (%Y-%m-%d)'))

    def get_absolute_url(self):
        # page 109
        return reverse('meeting-detail', kwargs={'pk': self.pk})

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
        else:
            return u' {0}, {1} or {2}.'.format(*contact_list)

    class Meta:
        abstract = True