# from collections import deque
import sys
from Queue import Queue, Empty
import threading
import time
from bibliopixel.led import *
from bibliopixel.drivers.APA102 import *
import numpy as np
from lights import RadioMeterLight, StripLed, LightBall
# from light_sensor import LightSensor
#from lux_sensor import LightSensor
from bh1750 import BH1750

# Thread targets
def msg_from_q(q, leds):
    while True:
        # something happened with the sensors, change direction
        msg = q.get() # blocks, so no need to sleep
        leds.consume_msg(msg)

def update_leds(leds):
    # lighten or darken the "next" led, depending on direction
    while True:
        leds.next()
        time.sleep(0.15)

def update_sensor(sensor):
    while True:
        sensor.update()
        #print(sensor.read())
        time.sleep(0.05)

# def print_q(leds):
#     while True:
#         print(leds.rising, leds.led_status)
#         time.sleep(1)
#
def send_msg_delayed(q):
    q.put("start")
    print("sent message START")
    time.sleep(40)
    q.put("stop")
    print("sent message STOP")
    time.sleep(40)
    q.put("start")
    print("sent message START")

class LedOrchestrator(object):
    def __init__(self, leds_array):
        self.rising = False
        self.leds = leds_array
        self.led_status = np.zeros(len(self.leds))

    def consume_msg(self, msg):
        if msg == "stop":
            self.rising = False
        elif msg == "start":
            self.rising = True

    def darken_next(self):
        try:
            #check status array and set the rightmost nonzero index to 0
            prev_i = np.nonzero(self.led_status)[0][-1]
            self.leds[prev_i].darken()
            self.led_status[prev_i] = 0
        except IndexError:
            return None

    def lighten_next(self):
        try:
            if len(np.nonzero(self.led_status)[0]) == 0: # all are dark
                next_i = 0
            else:
                next_i = np.nonzero(self.led_status)[0][-1] + 1
            self.leds[next_i].lighten()
            self.led_status[next_i] = 1
        except IndexError:
            # go next, so light the balls?
            return None

    def next(self):
        if self.rising:
            return self.lighten_next()
        else:
            return self.darken_next()

# closure to give to sensor as a callback
def put_msg_to_q(q, msg):
    def f():
        print(msg)
        q.put(msg)
    return f

if __name__ == '__main__':
    msg_q = Queue()
    msg_q.put("stop")

    sensor = BH1750()
    sensor.register_callback(put_msg_to_q(msg_q, 'start'), 50, 'rising')
    sensor.register_callback(put_msg_to_q(msg_q, 'stop'), 50, 'falling')

    num_leds = 221
    lit_delay = 0.05
    #dark_delay = 0.01
    dark_delay = 0
    driver = DriverAPA102(num_leds, use_py_spi=True, c_order=ChannelOrder.BGR)
    strip = LEDStrip(driver)

    # Construct array of light objects to correspond to the physical piece
    # 1. "light hose"
    leds = [StripLed(strip, i, lit_delay, dark_delay, (100,100,100)) for i in range(120)]
    # leds = [StripLed(strip, i, lit_delay, dark_delay) for i in range(20)]

    # 2. barrel
    # all consecutive
    # map(leds.append, [StripLed(strip, i, lit_delay) for i in range(120, 192)])
    # OR every other first and the the rest
    # map(leds.append, [StripLed(strip, i, 0.01, dark_delay, (1,1,1)) for i in range(120,176,2)])
    # map(leds.append, [StripLed(strip, i, 0.3, dark_delay) for i in range(121,176,2)])
    # OR only the "rodded" leds, picked out by trial and error
    # map(leds.append, [StripLed(strip, i, 0, dark_delay, (1,1,1)) for i in range(120,176)])
    leds.append(StripLed(strip, 122, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 129, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 136, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 143, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 150, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 157, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 164, lit_delay=0.5, dark_delay=0.5))
    leds.append(StripLed(strip, 171, lit_delay=0.5, dark_delay=0.5))

    # 3. radiometer superled
    #leds.append(RadioMeterLight())

    # 4. leds in the "exhaust" pipe
    map(leds.append, [StripLed(strip, i, lit_delay, dark_delay, (255,255,255)) for i in range(176, 222)])

    # 5. individual light balls at the end
    leds.append(LightBall('localhost', 1, 3))
    leds.append(LightBall('localhost', 2, 3))
    leds.append(LightBall('localhost', 3, 3))
    # map(leds.append, [StripLed(i) for i in range(10,100)])
    
    led_ctrl = LedOrchestrator(leds)

    # Whenever a message appears in the queue, this function passes it to the led orchestrator
    msg_thread = threading.Thread(target=msg_from_q, args=(msg_q,led_ctrl))
    msg_thread.daemon = True
    msg_thread.start()

    # This is a busy loop which iterates the leds (lights or darkens the "next" one)
    led_thread = threading.Thread(target=update_leds, args=(led_ctrl,))
    led_thread.daemon = True
    led_thread.start()

    # This is a busy loop which updates the sensor values
    # sensor_thread = threading.Thread(target=update_sensor, args=(sensor,))
    # sensor_thread.daemon = True
    # sensor_thread.start()

    # FOR TESTING --->
    # print_thread = threading.Thread(target=print_q, args=(led_ctrl,))
    # print_thread.daemon = True
    # print_thread.start()

    foo_thread = threading.Thread(target=send_msg_delayed, args=(msg_q,))
    foo_thread.daemon = True
    foo_thread.start()
    # <--- FOR TESTING

    #counter = 0

    # just keepin this main thread alive, threads are daemoned.
    try:
        while True:
            # I think this helps prevent CPU 100% all the time...
            # print('loop {}'.format(counter))
            #counter += 1
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        strip.fill((0,0,0))
        strip.update()
        # map(lambda l: l.darken(), leds)
        print("bye")
