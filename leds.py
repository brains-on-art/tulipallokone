# from collections import deque
import sys
from Queue import Queue, Empty
import threading
import time
# from bibliopixel.led import *
# from bibliopixel.drivers.LPD8806 import *
import numpy as np

N_LEDS = 100

def msg_from_q(q, leds):
    while True:
        msg = q.get()
        leds.consume_msg(msg)
        # try:
        #     msg = q.get(block=False)
        #     leds.consume_msg(msg)
        # except Empty:
        #     pass
        # leds.next()
        # time.sleep(0.5)

def update_leds(leds):
    while True:
        leds.next()
        time.sleep(0.5)

def print_q(leds):
    while True:
        print(leds.rising, leds.led_status)
        time.sleep(1)

class LedUtil():
    def __init__(self, n_leds):
        # self.driver = DriverLPD8806(104, use_py_spi=True, c_order=ChannelOrder.GRB)
        # self.strip = LEDStrip(driver)
        self.rising = False
        # self.dir_delta_t = time.time()
        self.led_status = np.zeros(n_leds)

    def consume_msg(self, msg):
        if msg == "stop":
            self.rising = False
            # self.dir_delta_t = time.time()
        elif msg == "start":
            self.rising = True
            # self.dir_delta_t = time.time()

    def recede_next(self):
        try:
            #check status array and set the rightmost nonzero index to 0
            prev_i = np.nonzero(self.led_status)[0][-1]
            # self.strip.set(prev_i, (50,50,50))
            self.led_status[prev_i] = 0
        except IndexError:
            return None

    def advance_next(self):
        try:
            if len(np.nonzero(self.led_status)[0]) == 0: # all are dark
                next_i = 0
            else:
                next_i = np.nonzero(self.led_status)[0][-1] + 1
            self.led_status[next_i] = 1
            # self.strip.set(next_i, (240,240,240))
        except IndexError:
            #move to the next steps
            return None

    def next(self):
        # print("next led")
        if self.rising:
            return self.advance_next()
        else:
            return self.recede_next()
        # self.strip.update()

def send_msg_delayed(q):
    time.sleep(10)
    q.put("stop")
    time.sleep(20)
    q.put("start")

if __name__ == '__main__':
    msg_q = Queue()
    msg_q.put("start")

    led_ctrl = LedUtil(N_LEDS)

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
            time.sleep(1)
        except KeyboardInterrupt:
            break
