from bibliopixel.led import *
from bibliopixel.drivers.APA102 import *
import time

if __name__=='__main__':
    num_leds = 40
    full_white = (55, 55, 55)
    dark = (0, 0, 0)

    driver = DriverAPA102(num_leds, use_py_spi=True, c_order=ChannelOrder.BGR)
    strip = LEDStrip(driver)

    dir = 1
    ind = 0

    strip.fill(dark)
    strip.set(0, full_white)
    strip.update()

    while True:
        ind = ind + (dir * 2)

        if ind <= 0:
            dir = 1
        elif ind >= num_leds:
            dir = -1
            ind = num_leds - 2
        
        if dir == 1:
            strip.set(ind, full_white)
            strip.update()
        else:
            strip.set(ind, dark)
            strip.update()

        time.sleep(0.2)

