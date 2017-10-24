from schedule.feeds.ical import ICalendarFeed
from schedule.models import Event

# A starting point:
# https://github.com/llazzaro/django-scheduler/blob/develop/schedule/feeds/__init__.py#L49

class TownICalendar(ICalendarFeed):
    def items(self):
        return Event.objects.filter(entity__jurisdiction__slug=slug).\
            order_by('-start')
