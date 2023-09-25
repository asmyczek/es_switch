
# -*- coding: utf-8 -*-

import unittest
from es_switch.switch import ESSwitch, PowerStatus
from datetime import datetime, timedelta


now = datetime.now()


def test_ls_event_callback():
    return [(now - timedelta(minutes=10), 
             now + timedelta(minutes=10))]

def test_no_ls_event_callback():
    return [(now + timedelta(minutes=10), 
             now + timedelta(minutes=20))]

test_switch_on_event_callback = [(now - timedelta(minutes=10),
                                  now + timedelta(minutes=10))]

test_switch_off_event_callback = [(now + timedelta(minutes=10), 
                                   now + timedelta(minutes=20))]


class TestPowerStatus(unittest.TestCase):

    def setUp(self):
        print("Initialising PowerStatus")
        power_status = PowerStatus()
        power_status.initialised = False
        power_status.power_on = False
        power_status.stage = -1
        power_status.block_times = None
        power_status.events_callback = None

    def test_initialisation(self):
        power_status = PowerStatus()

        # Not initialised
        self.assertEqual(power_status.initialised, False)

        # Update stage, not initialised
        power_status.update_stage(1)
        self.assertEqual(power_status.initialised, False)

        # Initialized with callback
        power_status.events_callback = test_ls_event_callback
        power_status.update_stage(1)
        self.assertEqual(power_status.initialised, True)

        # Reset callback, not initialised
        power_status.events_callback = None
        power_status.update_stage(2)
        self.assertEqual(power_status.initialised, False)

    def test_in_outage(self):
        power_status = PowerStatus()

        # Not initialised
        self.assertEqual(power_status.in_outage(), True)

        # Not initialised, status update
        power_status.update_stage(1)
        self.assertEqual(power_status.in_outage(), True)

        # Initialised, in load shedding
        power_status.events_callback = test_ls_event_callback
        power_status.update_stage(2)
        self.assertEqual(power_status.in_outage(), True)

        # Not in load shedding
        power_status.events_callback = test_no_ls_event_callback
        power_status.update_stage(3)
        self.assertEqual(power_status.in_outage(), False)

        # Status update, not in load shedding
        power_status.update_stage(0)
        self.assertEqual(power_status.in_outage(), False)


class TestSwitchOnOff(unittest.TestCase):

    def setUp(self):
        print("Initialising PowerStatus")
        power_status = PowerStatus()
        power_status.initialised = False
        power_status.power_on = False
        power_status.stage = -1
        power_status.block_times = None
        power_status.events_callback = None

        self.s1 = ESSwitch("S1", switch_callback=lambda x: None)

    def test_turn_on_off(self):
        power_status = PowerStatus()

        # Not initialised, switch off
        self.assertEqual(self.s1.on, False)
        self.s1.turn_on()
        self.assertEqual(self.s1.on, False)
        self.s1.turn_off()
        self.assertEqual(self.s1.on, False)

        # Initialised, in load shedding
        power_status.events_callback = test_ls_event_callback
        power_status.update_stage(2)
        self.s1.turn_on()
        self.assertEqual(self.s1.on, False)
        self.s1.turn_off()
        self.assertEqual(self.s1.on, False)

        # Initialised, not in load shedding
        power_status.events_callback = test_no_ls_event_callback
        power_status.update_stage(3)
        self.s1.turn_on()
        self.assertEqual(self.s1.on, True)
        self.s1.turn_off()
        self.assertEqual(self.s1.on, False)


    def test_turn_schedule(self):
        power_status = PowerStatus()
        self.assertEqual(self.s1.on, False)

        # Set in schedule time
        self.s1.schedule = test_switch_on_event_callback

        # Initialised, in load shedding, in schedule
        power_status.events_callback = test_ls_event_callback
        power_status.update_stage(2)
        self.s1.update_status()
        self.assertEqual(self.s1.on, False)

        # Initialised, no load shedding, in schedule
        power_status.events_callback = test_no_ls_event_callback
        power_status.update_stage(3)
        self.s1.update_status()
        self.assertEqual(self.s1.on, True)

        # Set off schedule time
        self.s1.schedule = test_switch_off_event_callback

        # Initialised, in load shedding, off schedule
        power_status.events_callback = test_ls_event_callback
        power_status.update_stage(0)
        self.s1.update_status()
        self.assertEqual(self.s1.on, False)

        # Initialised, no load shedding, off schedule
        power_status.events_callback = test_no_ls_event_callback
        power_status.update_stage(1)
        self.s1.update_status()
        self.assertEqual(self.s1.on, False)


if __name__ == "__main__":
    unittest.main()

