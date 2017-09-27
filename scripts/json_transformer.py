'''
Takes the whole JSON app dump from the old civic_calendar.meeting model and 
rearranges the JSON to reflect the tables of the new civic_calendar2 
schedule.event schema.
'''

# https://stackoverflow.com/questions/7127053/python-find-location-of-data-within-json-object-parse-the-corresponding-data

import json
import pprint

# from django.utils.text import slugify

with open('civic_calendar.json', 'r') as f:
    meeting_data = json.load(f)
with open('schedule.json', 'r') as s:
    schedule_data = json.load(s)

out_item_list = []

for item in schedule_data:
    # # Accessing python dict with multiple-key lookup string
    # # https://stackoverflow.com/questions/9320335/accessing-python-dict-with-multiple-key-lookup-string
    # key = "fields.entity"
    # foo = reduce(dict.get, key.split('.'), item)
    # print foo

    # First collect all the schedule.eventrelation entries ... 
    if item["model"] == "schedule.eventrelation":

        # from the eventrelation, get the ids of the the related schedule.event
        # and civic_calendar.meeting
        event_id = item["fields"]["event"]
        meeting_id = item["fields"]["object_id"]

        # munge through schedule_data (again) to get event
        my_events = [ my_event for my_event in schedule_data
            if my_event["model"] == "schedule.event" 
            and my_event["pk"] == event_id ]
        '''
        my_events

        [{u'fields': {u'calendar': 2,
                    u'color_event': None,
                    u'created_on': u'2016-10-27T20:48:18.607Z',
                    u'creator': 2,
                    u'description': u'Public hearing on proposed 2017 budgets, revenue requirements and prices; Carmen-Smith settlement agreement; and avoided cost filing.',
                    u'end': u'2016-11-01T19:29:00Z',
                    u'end_recurring_period': None,
                    u'rule': None,
                    u'start': u'2016-11-01T17:30:00Z',
                    u'title': u'Eugene Water & Electric Board meeting',
                    u'updated_on': u'2016-10-27T20:51:12.529Z'},
        u'model': u'schedule.event',
        u'pk': 15}]
        '''

        meeting_fields = [ my_meeting["fields"] for my_meeting in meeting_data 
            if my_meeting["model"] == "civic_calendar.meeting" 
            and my_meeting["pk"] == meeting_id ]
        '''
        meeting_fields

        [{u'agenda': u'Public hearing on proposed 2017 budgets, revenue requirements and prices; Carmen-Smith settlement agreement; and avoided cost filing.',
        u'contact_email': u'',
        u'contact_phone': u'541-685-7191',
        u'created': u'2016-10-27T20:48:18.595Z',
        u'entity': 1,
        u'location': 1,
        u'start': u'2016-11-01T17:30:00Z',
        u'website': u'www.eweb.org'}]
        '''

        my_events[0]["fields"][u"entity"] = meeting_fields[0]["entity"]
        my_events[0]["fields"][u"location"] = meeting_fields[0]["location"]
        my_events[0]["fields"][u"agenda"] = meeting_fields[0]["agenda"]
        my_events[0]["fields"][u"contact_email"] = meeting_fields[0]["contact_email"]
        my_events[0]["fields"][u"contact_phone"] = meeting_fields[0]["contact_phone"]
        my_events[0]["fields"][u"created"] = meeting_fields[0]["created"]
        my_events[0]["fields"][u"website"] = meeting_fields[0]["website"]
        my_events[0]["fields"][u"color_event"] = u""

        # pprint.pprint(my_events)

        out_item_list.append(my_events[0])

        # for schedule_item in schedule_data:
        #     if schedule_item["model"] == "schedule.eventrelation" and \
        #         schedule_item["pk"] == schedule_item["pk"]:
        #             my_event_id = schedule_item['fields']['event']
        #             # pprint.pprint(schedule_item)

        #     for schedule_item in schedule_data:
        #         if schedule_item["model"] == "schedule.event" and \
        #             schedule_item["pk"] == my_event_id:
        #             pprint.pprint(item)
        #             pprint.pprint(schedule_item)
        #             break

with open('munged_schedule_event.json', 'w') as out_file:
    json.dump(out_item_list, out_file, sort_keys=True, indent=2)

