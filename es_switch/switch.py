# -*- coding: utf-8 -*-
'''
ES push API to control geyser when or power.
'''

from datetime import datetime, timedelta


def in_time_range(dtime, schedule):
    for (start, end) in schedule:
        if start < dtime < end:
            return True
    return False


'''
Power Status singleton
'''
class PowerStatus(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PowerStatus, cls).__new__(cls)
        return cls.instance
        
    def __init__(self):
        if not hasattr(self, 'initialised'):
            self.initialised = False    # False on start and if API calls to espush or escome faile, swicht will always stay off
            self.power_on = False       # Status of power line, off on start, if API calls fails or during load shedding, switch stays off
            self.stage = -1             # Current loadshedding stage, only correct if initialised in True
            self.block_times = None     # List of next block times when switch stays off, only correct if initialised in True
            self.events_callback = None # Provide custom API callback

    def __str__(self):
        return f"PowerStatus: ({self.initialised}, {self.power_on}, {self.stage}, {self.block_times})"
        
    def _outage_times(self, events, time_buffer=10):
        outages = []
        for (start, end) in events:
            outages.append((start - timedelta(minutes=time_buffer),
                            end + timedelta(minutes=time_buffer)))
        return outages
    
    def in_outage(self, dtime=datetime.now()):
        return not self.initialised or in_time_range(dtime, self.block_times)

    def update_stage(self, stage):
        if stage is None:
            self.initialised = False
        elif stage != self.stage:
            try:
                self.block_times = self._outage_times(self.events_callback())
                self.stage = stage
                self.initialised = True
            except Exception as e:
                print(e)
                self.initialised = False
        
    def update_power_status(self, power_on):
        self.power_on = power_on


class ESSwitch:

    def __init__(self, id, switch_callback=None, schedule=[]):
        self.id = id
        self.schedule = schedule
        self._on = False
        self._switch_callback = switch_callback
    
    def __str__(self):
        return f"LSSwitch {self.id}: ({self._on}, {self.schedule})"

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, turn_on):
        on = turn_on and not PowerStatus().in_outage()
        if self._on != on:
            self._on = on
            if self._switch_callback:
                self._switch_callback(on)
            else:
                print("Switch callback not set!")

    def turn_on(self):
        self.on = True

    def turn_off(self):
        self.on = False

    def update_status(self):
        on = in_time_range(datetime.now(), self.schedule) and not PowerStatus().in_outage()
        if on != self.on:
            self.on = on

