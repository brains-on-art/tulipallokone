from Adafruit_PureIO import smbus


def read_2byte(self, addr):
    """Read a single byte from the specified device."""
    assert self._device is not None, 'Bus must be opened before operations are made against it!'
    self._select_device(addr)
    return [ord(x) for x in self._device.read(2)]
smbus.SMBus.read_2byte = read_2byte


import time


BH1750_ADDRESS = 0x23 #default I2C address
POWER_DOWN     = 0x00
POWER_ON       = 0x01
RESET          = 0x07
CONTINUOUS_HIGH_RES_MODE  = 0x10
CONTINUOUS_HIGH_RES_MODE2 = 0x11
CONTINUOUS_LOW_RES_MODE   = 0x13
ONE_TIME_HIGH_RES_MODE    = 0x20
ONE_TIME_HIGH_RES_MODE2   = 0x21
ONE_TIME_LOW_RES_MODE     = 0x23
MTREG_HIGH = 0x40 # 0100 0xxx
MTREG_LOW  = 0x60  # 011x xxxx



class BH1750(object):
    # def __init__(self, adc_channel=0, adc_gain=1, adc=None):
    def __init__(self, address=BH1750_ADDRESS, bus=None, **kwargs):
        self.address = address
        if bus is None:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = bus

        # self.running = False

        #if i2c is None:
        #   import Adafruit_GPIO.I2C as I2C
        #    i2c = I2C
        #self._device = i2c.get_i2c_device(address, **kwargs)

        self.bus.write_byte(address, CONTINUOUS_HIGH_RES_MODE)
        time.sleep(0.2)

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
        #data = self._device._bus.read_i2c_block_data(self.addr, ONE_TIME_HIGH_RES_MODE)
        data = self.bus.read_2byte(self.address)
        #print(type(data), len(data))
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
    l = BH1750()

    print('BH1750 sensor demo!')

    def f():
        print('Light sensor signal above 100 lux!')
    def g():
        print('Light sensor signal below 50 lux!')

    l.register_callback(f, 100, 'rising')
    l.register_callback(g, 50, 'falling')

    # l.start()

    while True:
        l.update()
        # print(l.read(), l.old_value)
        time.sleep(0.01)
