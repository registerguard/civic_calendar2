# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import pytz

from braces.views import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
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
        event = form.save()
        # end = meeting.start + datetime.timedelta(minutes=119)
        # event = Event(
            # start=meeting.start,
            # end=end,
            # title=u'{0} meeting'.format(meeting.entity.name),
            # description=meeting.agenda,
            # May need to get entity and location from form here, 
            # rather than __init__ values from forms.py ... JH, 7/26/17
        # )
        event.creator=self.request.user
        event.save()
        # er = EventRelation.objects.create_relation(event, meeting)
        # er.save()
        try:
            cal = Calendar.objects.get(name='civic')
        except Calendar.DoesNotExist:
            error_msg = "Calendar object not found."
            raise Calendar.DoesNotExist(error_msg)

        cal.events.add(event)
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
        event_id_list = [occurrence.event_id for occurrence in upcoming.get_occurrences()]
        return EventRelation.objects.filter(event_id__in=event_id_list)


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
        # self.object = self.get_object()
        # meeting = Meeting.objects.get(pk=self.object.content_object.id)
        event = Event.objects.get(pk=self.id)
        if event.creator == request.user:
            event.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404('You are not the owner of this event.')

