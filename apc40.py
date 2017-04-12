#!/usr/bin/env python3

import time
import rtmidi
import random
from time import sleep

TRACK_COUNT = 8

class Knob():
    CHAN_BASE = 0xB0

    """Knobs have positions indicated by the LEDs"""
    def __init__(self, m_out, knob_ctrl_id):
        self._m_out = m_out
        self._knob_ctrl_id = knob_ctrl_id
        self._led_ctrl_id = knob_ctrl_id + 0x8
        self._position = [0] * TRACK_COUNT
        self._led_ring_type = 1

        self.position = self._position
        self.led_ring_type = self._led_ring_type

    def set_position(self, track, v):
        if (track < 0 or track > 8):
            raise ValueError

        if (v < 0 or v > 127):
            raise ValueError

        # track is mapped to midi channel
        chan = self.CHAN_BASE + track
        self._m_out.send_message([chan, self._knob_ctrl_id, v])
        self._position[track] = v


    def set_led_ring_type(self, track, v):
        chan = self.CHAN_BASE + track
        self._m_out.send_message([chan, self._led_ctrl_id, v])

    def add_saturate(self, track, v):
        if (track < 0 or track > 8):
            raise ValueError
        pos = self._position[track] + v
        if pos > 127:
            pos = 127
        self.set_position(track, pos)

    def sub_saturate(self, track, v):
        if (track < 0 or track > 8):
            raise ValueError
        pos = self._position[track] - v
        if pos < 0:
            pos = 0
        self.set_position(track, pos)

class Button():
    """Button types can be multicolor, unicolor, or plain"""
    def __init__(self, m_out, channel, note, type):
        self._m_out = m_out
        self._channel = channel
        self._note = note

    @property
    def velocity(self):
        pass

    @velocity.setter
    def velocity(self, v):
        self._m_out.send_message([self._channel, self._note, self._velocity])


class Slider():
    def __init__(self, id):
        self._id = id

    @property
    def value(self):
        return None

class ClipLaunchGrid():
    def __init__(self):
        pass


#class ClipStopBar():
#    pass
#
#class SceneLaunchBar():

class APC40():
    CLIP_LAUNCH_1 = 0x35

    def __init__(self):
        self._m_in = rtmidi.MidiIn()
        self._m_out = rtmidi.MidiOut()

        # Look up the input/output port IDs for the APC40
        try:
            self.p_in = \
                [i for i, s in enumerate(self._m_in.get_ports())
                    if 'APC40' in s][0]
            self.p_out = \
                [i for i, s in enumerate(self._m_out.get_ports())
                    if 'APC40' in s][0]
        except:
            print("APC40 not found!")
            return None

        # Open the ports
        self._m_in.open_port(self.p_in)
        self._m_out.open_port(self.p_out)

        self._m_in.set_callback(self)




    def __call__(self, event, data=None):
        message, deltatime = event
        print("[%s] @%0.6f %r" % (self._m_in, deltatime, message))

    def write(self, channel, note, velocity):
        self._m_out.send_message([channel, note, velocity])

    # NOTE: index on board starts from one, not zero.
    def clip_launch_led(self, x, y, color):
        if (x < 1 or x > 8):
            raise ValueError
        if (y < 1 or y > 5):
            raise ValueError
        channel = 0x90 + x - 1
        note = self.CLIP_LAUNCH_1 + y - 1
        velocity = color
        self.write(channel, note, velocity)

if __name__ == "__main__":
    apc = APC40()
    dc_knobs = []
    tc_knobs = []

    # random '53,73' range is to try to center around 127/2 (with some variation)
    # This makes the random dial animations look cooler.
    for i in range(0, 8):
        dck = Knob(apc._m_out, 0x10 + i)
        dck.set_led_ring_type(0, 3)
        dck.set_position(0, random.randint(53, 73))
        dc_knobs.append(dck)

        tck = Knob(apc._m_out, 0x30 + i)
        tck.set_led_ring_type(0, 1)
        tck.set_position(0, random.randint(53, 73))
        tc_knobs.append(tck)

    idx = 0
    step = 8
    while(1):
        for x in range(0, 8):
            for y in range(0, 5):
                apc.clip_launch_led(x+1,y+1,random.randint(1,6) | 1)

        for k in dc_knobs:
            if (k._position[0] > 63):
                k.add_saturate(0, step)
            else:
                k.sub_saturate(0, step)
            if k._position[0] <= 0 or k._position[0] >= 127:
                k.set_position(0, random.randint(53, 73))

        for k in tc_knobs:
            if (k._position[0] > 63):
                k.add_saturate(0, step)
            else:
                k.sub_saturate(0, step)

            if k._position[0] <= 0 or k._position[0] >= 127:
                k.set_position(0, random.randint(53, 73))


        # idx += step
        # if idx > (127 + step):
        #     for k in dc_knobs:
        #         k.set_position(0, random.randint(0, 127))
        #     for k in tc_knobs:
        #         k.set_position(0, random.randint(0, 127))
        #     idx = 0
        sleep(.1)
