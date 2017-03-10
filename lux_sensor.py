from Adafruit_PureIO import smbus
import time

DEVICE = 0x23 #default I2C address
POWER_DOWN = 0x00
POWER_ON = 0x01
RESET = 0x07
ONE_TIME_HIGH_RES_MODE = 0x20

# bus = smbus.SMBus(1)

# def main():
#     while True:
#         print("Light level: " + str(readLight()) + " lux")
#         time.sleep(0.5)


class LightSensor(object):
    # def __init__(self, adc_channel=0, adc_gain=1, adc=None):
    def __init__(self, addr=DEVICE):
        self.addr = addr
        self.bus = smbus.SMBus(1)

        # self.running = False

        self.value = None
        self.old_value = None

        self.rising_thresholds = []
        self.falling_thresholds = []

    # def start(self):
    #     self.adc.start_adc(self.adc_channel, self.adc_gain)
    #     self.running = True
    #
    # def stop(self):
    #     self.adc_stop()
    #     self.running = False

    # def read(self):
    #     if self.running:
    #         val = self.adc.get_last_result()
    #     else:
    #         val = self.adc.read_adc(self.adc_channel, gain=self.adc_gain)
    #     self.value, self.old_value = val, self.value
    #     return val

    def read(self):
        data = self.bus.read_i2c_block_data(self.addr, ONE_TIME_HIGH_RES_MODE)
        val = self.convertToNumber(data)
        self.value, self.old_value = val, self.value
        return val

    def update(self):
        value = self.read()
        old_value = self.old_value
        print('updating value for sensor: cur value {}, old value {}'.format(value, old_value))
        # Rising value
        if value > old_value:
            for x,f in self.rising_thresholds:
                if x > old_value and x < value:
                    f()
        if value < old_value:
            for x,f in self.falling_thresholds:
                if x < old_value and x > value:
                    f()
        return value

    def convertToNumber(self, data):
        return ((data[1] + (256 * data[0])) / 1.2)

    def register_callback(self, f, threshold, threshold_type='both'):
        print('callback registered')
        if threshold_type in ['rising', 'both']:
            self.rising_thresholds.append((threshold, f))
        if threshold_type in ['falling', 'both']:
            self.falling_thresholds.append((threshold, f))

if __name__ == '__main__':
    l = LightSensor()

    print('Lux sensor demo!')

    def f():
        print('Light sensor signal above 20000!')
    def g():
        print('Light sensor signal below 5000!')

    l.register_callback(f, 100, 'rising')
    l.register_callback(g, 50, 'falling')

    # l.start()

    while True:
        l.update()
        # print(l.read(), l.old_value)
        time.sleep(0.15)
