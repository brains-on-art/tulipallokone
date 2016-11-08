# from collections import deque
import sys
from Queue import Queue, Empty
import threading
import time
# from bibliopixel.led import *
# from bibliopixel.drivers.LPD8806 import *
import numpy as np

N_LEDS = 100

# Thread targets
def msg_from_q(q, leds):
    # something happened with the sensors, change direction
    while True:
        msg = q.get() # blocks, so no sleep
        leds.consume_msg(msg)

def update_leds(leds):
    # timer to advance to chosen direction
    while True:
        leds.next()
        time.sleep(0.5)

def print_q(leds):
    while True:
        print(leds.rising, leds.led_status)
        time.sleep(1)

def send_msg_delayed(q):
    time.sleep(20)
    q.put("stop")
    time.sleep(30)
    q.put("start")

class RadioMeterLight(object):
    def __init__(self):
        # self.driver = Adafruit_PCA9685.PCA9685()
        print('Assuming PWM frequency 60 Hz')
        # self.driver.set_pwm_freq(60)

    def lighten(self):
        # self.driver.set_pwm(self.pan_channel, 0, pulse) #TODO
        print("radiometer light lit")
        time.sleep(10)
        return

    def darken(self):
        # self.driver.set_pwm(self.pan_channel, 0, pulse) #TODO
        time.sleep(0.5)
        print("radiometer light darkened")

class StripLed(object):
    def __init__(self, index):
        # self.driver = DriverLPD8806(104, use_py_spi=True, c_order=ChannelOrder.GRB)
        # self.strip = LEDStrip(driver)
        self.index = index

    def lighten(self):
        time.sleep(0.5)
        print(self.index, "lit")
        # self.strip.set(self.i, (240,240,240))

    def darken(self):
        time.sleep(0.5)
        print(self.index, "darkened")
        # self.strip.set(self.i, (50,50,50))

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
            #move to the next steps
            return None

    def next(self):
        # print("next led")
        if self.rising:
            return self.lighten_next()
        else:
            return self.darken_next()
        # self.strip.update()

if __name__ == '__main__':
    msg_q = Queue()
    msg_q.put("start")

    leds = [StripLed(i) for i in range(10)]
    leds.append(RadioMeterLight())
    map(leds.append, [StripLed(i) for i in range(10,100)])

    # led_ctrl = LedOrchestrator(N_LEDS)
    led_ctrl = LedOrchestrator(leds)

    msg_thread = threading.Thread(target=msg_from_q, args=(msg_q,led_ctrl))
    msg_thread.daemon = True
    msg_thread.start()

    led_thread = threading.Thread(target=update_leds, args=(led_ctrl,))
    led_thread.daemon = True
    led_thread.start()

    # FOR TESTING --->
    print_thread = threading.Thread(target=print_q, args=(led_ctrl,))
    print_thread.daemon = True
    print_thread.start()

    foo_thread = threading.Thread(target=send_msg_delayed, args=(msg_q,))
    foo_thread.daemon = True
    foo_thread.start()
    # <--- FOR TESTING

    while True:
        try:
            time.sleep(0.01)
        except KeyboardInterrupt:
            break
