#!/usr/bin/env python3
# encoding: utf-8


"""
A simple little programm
to
copy future events into a new calendar
and
like that get rid of old calendar events
in
case of breach, hack, opsec
don't leak all your past

Released as is under
GPLv3

by
Felix
"""


import sys
import datetime
import icalendar
import recurring_ical_events


def print_event(calendar_event):
    """ Print: START - END: SUMMARY """
    estart = calendar_event.decoded("DTSTART")
    eend = calendar_event.decoded("DTEND")
    esummary = calendar_event.get("SUMMARY")
    print(f"\r{estart} - {eend}: {esummary}")

def future_events(ical_file):
    """ Open calendar file, expand recurring events
        Returns: event count, list of events """
    with open(ical_file, mode='r', encoding='utf-8') as c_file:
        c = icalendar.Calendar.from_ical(c_file.read())
    events = recurring_ical_events.of(c).between(datetime.datetime.today(),
                                                 until_end)
    count = len(events)
    return (count, events)

def copy_future_events(calendar_original, after):
    """ Copy future events into a new calendar
        Returns: new_calendar, count(events_in), count(events_out) """
    after_day = after.date()

    # create empty calendar to receive future events
    calendar_out = icalendar.Calendar()

    # counters
    events_in = 0
    events_out = 0

    for event in calendar_original.walk('VEVENT'):
        start = event.decoded("DTSTART")
        end = event.decoded("DTEND")
        recurr = event.get("RRULE", None)

        events_in = events_in + 1

        # is a recurring event
        if recurr:
            # a new calendar
            tmp_cal = icalendar.Calendar()
            # with only this event
            tmp_cal.add_component(event)
            # datetime of the end of the last of all events until max 01.01.2038
            last = recurring_ical_events.of(tmp_cal).between(after_day,
                       recurring_ical_events.DATE_MAX)
            if len(last) == 0:
                continue
            last = last[-1].get('DTEND').dt

            if isinstance(last, datetime.datetime) and last < after:
                continue

            # if it's an all day event
            # pylint: disable=C0123
            #     Use isinstance() rather than type() for a typecheck
            #     isinstance will give the wrong result due to the relationship
            if type(last) == datetime.date and last < after_day:
                continue

        # An event that lasts the entire day already has start and end as date
        # otherwise it is type datetime which can not be compared to date
        if isinstance(start, datetime.datetime):
            start = start.date()
            end = end.date()

        # if we reach this line and recurr is set the event continues into
        # the future
        if recurr or ( after_day < start or after_day < end ):
            calendar_out.add_component(event)
            events_out = events_out + 1

    return (calendar_out, events_in, events_out)

def compare_eventlists(l1, l2):
    """ Compare l1 to l2 if all events from l1 are contained in l2
        Returns: list(missing), list(invented) """
    s1 = [e.to_ical() for e in l1]
    s2 = [e.to_ical() for e in l2]
    outer = set(s1) ^ set(s2)

    if len(outer) == 0:
        return [], []

    missing = []
    invention = []
    for e_txt in outer:
        event = icalendar.Event().from_ical(e_txt)
        if e_txt in s1:
            missing.append(event)
        elif e_txt in s2:
            invention.append(event)
    return missing, invention

def self_test():
    """ Run some tests to check if everything works as designed """

    # the hypothetical test date TODAY
    after = datetime.datetime(2024, 4, 15, 12, 0, 0,
                              tzinfo=datetime.timezone.utc)

    test_calendar = icalendar.Calendar()
    event = icalendar.Event()

    # in the past and over
    event = icalendar.Event()
    event["SUMMARY"] = "Test1"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2010, 1, 1, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2010, 1, 1, 14, 00,
                         tzinfo=datetime.timezone.utc))
    test_calendar.add_component(event)

    # in the future and not started
    event = icalendar.Event()
    event["SUMMARY"] = "Test2"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2025, 1, 1, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2025, 1, 1, 14, 00,
                         tzinfo=datetime.timezone.utc))
    test_calendar.add_component(event)

    # started in the past and continues into the future
    event = icalendar.Event()
    event["SUMMARY"] = "Test3"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2024, 1, 1, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2024, 7, 1, 14, 00,
                         tzinfo=datetime.timezone.utc))
    test_calendar.add_component(event)

    # recurring events
    # daily starts in the past and continues into the future
    event = icalendar.Event()
    event["SUMMARY"] = "Test4"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2024, 4, 14, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2024, 4, 14, 14, 00,
                         tzinfo=datetime.timezone.utc))
    event["RRULE"] = icalendar.vRecur({'FREQ': ['DAILY'], 'COUNT': [5]})
    test_calendar.add_component(event)

    # yearly starts in the future and continues
    event = icalendar.Event()
    event["SUMMARY"] = "Test5"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2024, 7, 14, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2024, 7, 14, 14, 00,
                         tzinfo=datetime.timezone.utc))
    event["RRULE"] = icalendar.vRecur({'FREQ': ['YEARLY'], 'COUNT': [2]})
    test_calendar.add_component(event)

    # daily starts in the past and stays in the past
    event = icalendar.Event()
    event["SUMMARY"] = "Test6"
    event["DTSTART"] = icalendar.vDDDTypes(datetime.datetime(2023, 7, 14, 12, 00,
                           tzinfo=datetime.timezone.utc))
    event["DTEND"] = icalendar.vDDDTypes(datetime.datetime(2023, 7, 14, 14, 00,
                         tzinfo=datetime.timezone.utc))
    event["RRULE"] = icalendar.vRecur({'FREQ': ['DAILY'], 'COUNT': [4]})
    test_calendar.add_component(event)

    test_calendar_out, _, _ = copy_future_events(test_calendar, after)

    titles = [e["SUMMARY"] for e in test_calendar_out.walk('VEVENT')]

    fault = False
    def err(summary, value):
        if summary in titles == value:
            print(f"KeyError: {summary}")
            fault = True

    err("Test1", True)
    err("Test2", False)
    err("Test3", False)
    err("Test4", False)
    err("Test5", False)
    err("Test6", True)

    events_in = (recurring_ical_events.of(test_calendar)
                    .between(after, recurring_ical_events.DATE_MAX))
    events_out = (recurring_ical_events.of(test_calendar_out)
                     .between(after, recurring_ical_events.DATE_MAX))

    found1, found2 = compare_eventlists(events_in, events_out)

    if len(found1) != 0:
        print(KeyError("Test7"))
        fault = True
    if len(found2) != 0:
        print(KeyError("Test8"))
        fault = True

    if fault:
        raise KeyError("Test(s) failed")

    return not fault


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <in-calendar.ics> <out-calendar.ics>")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2]


    # SELF TEST
    if self_test():
        print("Selftest OK")


    # DO THE WORK
    # read calendar file to calendar
    with open(in_file, mode='r', encoding='utf-8') as calendar_file:
        calendar_in = icalendar.Calendar.from_ical(calendar_file.read())

    from_now = datetime.datetime.now().astimezone()
    c_out, e_in, e_out = copy_future_events(calendar_in, from_now)

    # write reduced copy
    with open(out_file, mode='wb') as calendar_file:
        calendar_file.write(c_out.to_ical())

    print(f"Read {e_in} events")
    print(f"Wrote {e_out} events")


    # VERIFY
    # we will not find errors in the used python modules

    until_end = recurring_ical_events.DATE_MAX
    print(f"Double check future events until {until_end}")

    n_list_in, events_list_in = future_events(in_file)
    print(f"Expanded future events in \"{in_file}\": {n_list_in}")

    n_list_out, events_list_out = future_events(out_file)
    print(f"Expanded future events in \"{out_file}\": {n_list_out}")

    # there might be missing AND invented events
    print("Look for missed and invented events")
    missed, invented = compare_eventlists(events_list_in, events_list_out)

    if missed:
        print("Missing events:")
        for e in missed:
            print_event(e)

    if invented:
        print("Invented events:")
        for e in invented:
            print_event(e)

    print("Done")
