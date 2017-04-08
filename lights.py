import time
import paho.mqtt.client as mqtt

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
    def __init__(self, strip, index, lit_delay=0.5, dark_delay=0.5, default_lit_brightness=(255,255,255)):
        self.strip = strip
        self.i = index
        self.strip.set(self.i, (0,0,0))
        self.strip.update()
        self.lit_delay = lit_delay
        self.dark_delay = dark_delay
        self.lit_brightness = default_lit_brightness

    def lighten(self, brightness=None):
        if not brightness:
            brightness = self.lit_brightness

        self.strip.set(self.i, brightness)
        self.strip.update()
        time.sleep(self.lit_delay)

    def darken(self):
        # print(self.i, "darkened")
        self.strip.set(self.i, (0,0,0))
        self.strip.update()
        time.sleep(self.dark_delay)

class LightBall(object):
    def __init__(self, host, ball_id, lit_delay=0.5, dark_delay=0.5):
        self.client = mqtt.Client()
        self.host = host
        self.ball_id = ball_id
        self.lit_delay = lit_delay
        self.dark_delay = dark_delay

    def lighten(self):
        self.client.connect(self.host, 1883, 1)
        self.client.publish("/lights/{}".format(self.ball_id), "1")
        print("ball led ", self.ball_id, "lit")
        time.sleep(self.lit_delay)

    def darken(self):
        self.client.connect(self.host, 1883, 1)
        self.client.publish("/lights/{}".format(self.ball_id), "0")
        print("ball led", self.ball_id, "darkened")
        time.sleep(self.dark_delay)
