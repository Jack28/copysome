# copysome

PROTOTYPE!!!


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


 - Recurring events are handled
 - From today onwards
 - Call it opsec
 - Data is waste: save the planet


## Installation

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Usage

    Usage: ./copysome.py <in-calendar.ics> <out-calendar.ics>

### Example

    $ ./copysome.py Kalender.ics out.ics
    Selftest OK
    Read 4241 events
    Wrote 119 events
    Double check future events until (2038, 1, 1)
    Expanded future events in "Kalender.ics": 2867
    Expanded future events in "out.ics": 2867
    Look for missed and invented events
    Done
