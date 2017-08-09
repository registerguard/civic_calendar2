# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import operator
import pytz

from braces.views import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic  import CreateView, DeleteView, ListView, UpdateView
from schedule.models import Calendar, Event
from schedule.periods import Period
from .forms import MeetingCreateViewForm
from .models import Meeting

class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = MeetingCreateViewForm
    # if no success_url, defaults to model object get_absolute_url(), if
    # available https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-editing/#model-forms
    success_url = reverse_lazy('meeting-list')

    # passing request.user to MeetingCreateViewForm
    def get_form_kwargs(self):
        kwargs = super(MeetingCreateView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.title = u'{0} meeting'.format(form.instance.entity)
        form.instance.creator = self.request.user
        form.instance.end = form.instance.start + \
            datetime.timedelta(minutes=119)
        try:
            form.instance.calendar = Calendar.objects.get(name='civic')
        except Calendar.DoesNotExist:
            error_msg = "Calendar object not found."
            raise Calendar.DoesNotExist(error_msg)

        return super(MeetingCreateView, self).form_valid(form)


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = MeetingCreateViewForm
    success_url = reverse_lazy('meeting-list')

    def get_form_kwargs(self):
        kwargs = super(MeetingUpdateView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.end = form.instance.start + \
            datetime.timedelta(minutes=119)
        try:
            cal = Calendar.objects.get(name='civic')
            form.instance.calendar = cal
        except Calendar.DoesNotExist:
            error_msg = "Calendar does not exist."
            raise Calendar.DoesNotExist(error_msg)

        return super(MeetingUpdateView, self).form_valid(form)


class MeetingListView(LoginRequiredMixin, ListView):
    '''
    For entities to see a list of their own meetings.
    '''
    login_url = reverse_lazy('login')
    template_name = 'civic_calendar/eventrelation_list.html'

    def get_queryset(self):
        return Event.objects.filter(creator=self.request.user)


class WebMeetingListView(ListView):
    '''
    Provide a Web view listing for public consumption.
    '''
    template_name = 'civic_calendar/meeting_list.html'

    def get_queryset(self):
        pacific = pytz.timezone('US/Pacific')
        my_events = Event.objects.all()
        my_today = pacific.localize(
            datetime.datetime.now().replace(hour=0, minute=0) \
        )
        upcoming = Period(
            my_events, my_today, my_today+datetime.timedelta(days=30)
        )
        ordered = sorted(
            upcoming.get_occurrences(),
            key=operator.attrgetter(
                'event.entity.jurisdiction.name',
                'event.start',
                'event.entity.name',
            )
        )
        return ordered

    def get_context_data(self, **kwargs):
        context = super(WebMeetingListView, self).get_context_data(**kwargs)
        context['page'] = {'title': '<a href="//registerguard.com/rg/news/local/">Local</a>', 'description_short': 'Calendar',}
        return context


class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    '''
    Deleting schedule.Event removes relevant:
        schedule.EventRelation
        schedule.Occurrence
        schedule.Event

        ... so just need to delete schedule.Event and civic_calendar.Meeting
    '''
    success_url = reverse_lazy('meeting-list')
    template_name = 'civic_calendar/confirm_delete.html'
    model = Event

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # meeting = Meeting.objects.get(pk=self.object.content_object.id)
        event = Event.objects.get(pk=self.object.id)
        if event.creator == request.user:
            event.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404('You are not the owner of this event.')


class OccurrenceListView(ListView):
    '''
    Display online meetings list/outputs InDesign-formatted text
    '''
    template_name = 'civic_calendar/occurrence_list.html'
    pacific = pytz.timezone('US/Pacific')

    def get_queryset(self):
        custom_date = self.request.GET.get('date', '')

        if custom_date:
            tomorrow = self.pacific.localize(
                datetime.datetime.strptime(custom_date, '%Y%m%d') + \
                datetime.timedelta(days=1)
            )
        else:
            tomorrow = self.pacific.localize(
                datetime.datetime.now().replace(hour=0, minute=0) + \
                datetime.timedelta(days=1)
            )

        my_events = Event.objects.all()
        upcoming = Period(
            my_events, tomorrow, tomorrow + datetime.timedelta(days=2)
        )

        occurrence_list = upcoming.get_occurrences()
        # sort by jurisdiction, start time, then name of entity
        # https://stackoverflow.com/questions/2412770/good-ways-to-sort-a-queryset-django
        ordered = sorted(
            occurrence_list,
            key=operator.attrgetter(
                'event.entity.jurisdiction.name',
                'event.start',
                'event.entity.name',
            )
        )

        for occurrence_item in ordered:
            # replace u'\r\n' with u' ' in Agenda text
            occurrence_item.event.agenda = \
                occurrence_item.event.agenda.replace(u'\r\n', u' ')

        return ordered

    def get_context_data(self, **kwargs):
        '''
        Returns a dictionary of context data
        '''
        request = self.request
        meetings = getattr(self, 'get_queryset', None)()

        if request.META['HTTP_USER_AGENT'].count('Macintosh'):
            client_os = u'MAC'
        else:
            client_os = u'WIN'

        return {
            'event_list': meetings,
            'os': client_os,
        }

    def get(self, *args, **kwargs):
        '''
        Set the HTTP response 'Content-Disposition' header & content_type and
        encode to utf-16le, the encoding that Adobe InDesign demands. 
        '''
        if self.get_context_data()['event_list']:
            # Serve Adobe InDesign-formatted file download.
            template = get_template(self.template_name)
            html = template.render(self.get_context_data())
            # Convert Unix line endings to Windows
            if self.get_context_data()['os'] == 'WIN':
                html = html.replace(u'\n', u'\r\n')
            html = html.encode('utf-16-le')
            response = HttpResponse(html, content_type='text/plain')
            response['Content-Disposition'] = \
                'attachment; filename=cr.calendar.txt'
        else:
            # Serve a plain 'ol web page if no upcoming meetings.
            template = get_template(
                'civic_calendar/occurrence_list_screen.html'
            )
            html = template.render(self.get_context_data())
            response = HttpResponse(html, content_type='text/html')
            response['Content-Disposition'] = 'inline'
        return response


class ProfileMeetingList(ListView):
    '''
    Event.objects.filter(creator__profile__slug='pretty-name-slug-here')
    '''
    model = Event
    template_name = 'civic_calendar/meeting_list_profile.html'

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Event.objects.filter(creator__profile__slug=slug).order_by('-start')

    def get_context_data(self, **kwargs):
        context = super(ProfileMeetingList, self).get_context_data(**kwargs)
        context['page'] = {'title': '<a href="//registerguard.com/rg/news/local/">Local</a>', 'description_short': '''<a href="{% url 'public-meeting-list' %}">Calendar</a>''',}
        return context
