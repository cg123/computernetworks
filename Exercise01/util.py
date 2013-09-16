#!/usr/bin/env python
# Copyright (c) 2013, Charles O. Goddard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import RPi.GPIO as gpio
import time

class AveragedSample(object):
    '''
    An average of a signal over the last N samples.
    '''
    def __init__(self, x0=0, samples=5):
        self.samples = [x0] * samples
        self.idx = 0

    def add(self, x):
        self.samples[self.idx] = x
        self.idx = (self.idx + 1) % len(self.samples)

    def evaluate(self):
        return sum(self.samples) / len(self.samples)


def measure_rc(pin, delay=0.005):
    # Bring pin low to discharge capacitor
    gpio.setup(pin, gpio.OUT)
    gpio.output(pin, gpio.LOW)
    time.sleep(delay)

    started = time.time()

    # Bring it high and measure the charge time
    gpio.setup(pin, gpio.IN)
    while not gpio.input(pin):
        if time.time() > started + delay:
            break
    return time.time() - started

def transmit(pin, data, delay=0.1):
    state = False
    gpio.setup(pin, gpio.OUT)
    gpio.output(pin, state)
    t0 = time.time()
    t1 = t0 + delay
    while time.time() < t1:
        pass
    t0 = t1

    bits = sum([[ord(c) & (1 << i) != 0 for i in range(8)] for c in data], [])
    for bit in bits:
        state = not state
        gpio.output(pin, state)

        t1 = t0 + (1.25 - (bit * 0.5)) * delay
        while time.time() < t1:
            pass
        t0 = t1
    state = not state
    gpio.output(pin, state)
    t1 = t0 + delay * 5
    while time.time() < t1:
        pass
    gpio.output(pin, False)


RCTHRESH = 0.000065

def receive(pin, delay=0.1):

    rc = AveragedSample(x0=0.0, samples=5)

    state = False
    # Gather initial samples and spin until we're in the state we expect
    while rc.idx < len(rc.samples) - 1 and (rc.evaluate() < RCTHRESH) != state:
        rc.add(measure_rc(pin))

    f = open('log.txt', 'a')
    pts = []

    last_change = 0
    while True:

        # If the input hasn't toggled in four periods, assume the stream has ended.
        if (last_change != 0 and time.time() > last_change + delay * 4):
            # Write out stored datapoints
            for t, rc in pts:
                f.write('%r %r\r\n' % (t, rc))
            f.close()

            return

        # Take a raw measurement and add it to the averager
        newrc = measure_rc(pin)
        rc.add(newrc)

        # If the stream has begun, log the current RC value
        if last_change != 0:
            pts.append([time.time(), newrc])

        # Check for state change
        new_state = rc.evaluate() < RCTHRESH  # TODO: make less arbitrary
        if new_state != state:
            if last_change == 0:
                last_change = time.time()
                state = new_state
            else:
                t = time.time()
                dt = t - last_change

                # Don't accept a state change until at least half a period has passed.
                if dt / delay < 0.5:
                	continue

                # Short pulse is True, long pulse is False
                if dt < delay:
                    yield True
                else:
                    yield False

                state = new_state
                last_change = time.time()
