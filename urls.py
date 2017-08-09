from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change,\
    password_change_done

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.MeetingListView.as_view(),
        name='meeting-list',
    ),
        url(
        regex=r'^print/$',
        view=views.OccurrenceListView.as_view(),
        name='upcoming-occurrences',
    ),
    url(
        regex=r'^add/$',
        view=views.MeetingCreateView.as_view(),
        name='create',
    ),
    url(
        regex=r'^(?P<pk>\d+)/update/$',
        view=views.MeetingUpdateView.as_view(),
        name='update',
    ),
    url(
        regex=r'^(?P<pk>\d+)/delete/$',
        view=views.MeetingDeleteView.as_view(),
        name='delete',
    ),
    url(
        regex=r'^meetings/$',
        view=views.WebMeetingListView.as_view(),
        name='public-meeting-list',
    ),
    url(
        regex=r'^meetings/$',
        view=views.WebMeetingListView.as_view(),
        name='public-meeting-list',
    ),
    url(
        regex=r'^meetings/(?P<slug>[-\w]+)/$',
        view=views.ProfileMeetingList.as_view(),
        name='profile-meeting-list',
    ),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': '/civic/'}, name='logout'),
    url(
        r'^password_change/$',
        password_change,
        {'template_name': 'registration/password_change.html'},
        name='password_change',
    ),
    url(
        r'^password_change/done/$',
        password_change_done,
        {'template_name': 'registration/password_changed.html'},
        name='password_change_done',
    ),
]