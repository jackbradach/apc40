#!/usr/bin/env python3

import time
import rtmidi
import random
from time import sleep

class APC40():
    CLIP_LAUNCH_1 = 0x35

    def __init__(self):
        self.m_in = rtmidi.MidiIn()
        self.m_out = rtmidi.MidiOut()

        # Look up the input/output port IDs for the APC40
        try:
            self.p_in = \
                [i for i, s in enumerate(self.m_in.get_ports())
                    if 'APC40' in s][0]
            self.p_out = \
                [i for i, s in enumerate(self.m_out.get_ports())
                    if 'APC40' in s][0]
        except:
            print("APC40 not found!")
            return None

        # Open the ports
        self.m_in.open_port(self.p_in)
        self.m_out.open_port(self.p_out)



    # NOTE: index on board starts from one, not zero.
    def clip_launch_led(self, x, y, color):
        if (x < 1 or x > 8):
            raise ValueError
        if (y < 1 or y > 5):
            raise ValueError
        channel = 0x90 + x - 1
        note = self.CLIP_LAUNCH_1 + y - 1
        velocity = color

        self.m_out.send_message([channel, note, velocity])


if __name__ == "__main__":
    apc = APC40()
    while(1):
        for x in range(0, 8):
            for y in range(0, 5):
                apc.clip_launch_led(x+1,y+1,random.randint(1,6) | 1)
        sleep(.1)
