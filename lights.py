import time

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
    def __init__(self, strip, index, delay=0.5):
        self.strip = strip
        self.i = index
        self.strip.set(self.i, (0,0,0))
	self.strip.update()
        self.delay = delay

    def lighten(self):
        # print(self.i, "lit")
        self.strip.set(self.i, (1,1,1))
	self.strip.update()
        time.sleep(self.delay)

    def darken(self):
        # print(self.i, "darkened")
        self.strip.set(self.i, (0,0,0))
	self.strip.update()
        time.sleep(self.delay)
