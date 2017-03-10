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
from lux_sensor import LightSensor

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
        time.sleep(0.2)

# def print_q(leds):
#     while True:
#         print(leds.rising, leds.led_status)
#         time.sleep(1)
# 
# def send_msg_delayed(q):
#     time.sleep(10)
#     q.put("stop")
#     time.sleep(30)
#     q.put("start")

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

    sensor = LightSensor()
    sensor.register_callback(put_msg_to_q(msg_q, 'start'), 50, 'rising')
    sensor.register_callback(put_msg_to_q(msg_q, 'stop'), 50, 'falling')
    # sensor.start()

    num_leds = 10
    delay = 0.3
    driver = DriverAPA102(num_leds, use_py_spi=True, c_order=ChannelOrder.BGR)
    strip = LEDStrip(driver)

    leds = [StripLed(strip, i, delay) for i in range(num_leds)]
    leds.append(LightBall('localhost', 1))
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
    sensor_thread = threading.Thread(target=update_sensor, args=(sensor,))
    sensor_thread.daemon = True
    sensor_thread.start()

    # FOR TESTING --->
    # print_thread = threading.Thread(target=print_q, args=(led_ctrl,))
    # print_thread.daemon = True
    # print_thread.start()

    # foo_thread = threading.Thread(target=send_msg_delayed, args=(msg_q,))
    # foo_thread.daemon = True
    # foo_thread.start()
    # <--- FOR TESTING

    counter = 0

    # just keepin this main thread alive, threads are daemoned.
    try:
        while True:
            # I think this helps prevent CPU 100% all the time...
            print('loop {}'.format(counter))
            counter += 1
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        strip.fill((0,0,0))
        strip.update()
        print("bye")
