import Adafruit_ADS1x15

class LightSensor(object):
    def __init__(self, adc_channel=0, adc_gain=1, adc=None):
        if adc is None:
            self.adc = Adafruit_ADS1x15.ADS1115()
        else:
            self.adc = adc

        self.adc_channel = adc_channel
        self.adc_gain = adc_gain

        self.running = False
        
        self.value = None
        self.old_value = None

        self.rising_thresholds = []
        self.falling_thresholds = []
    
    def start(self):
        self.adc.start_adc(self.adc_channel, self.adc_gain)
        self.running = True

    def stop(self):
        self.adc_stop()
        self.running = False

    def read(self):
        if self.running:
            val = self.adc.get_last_result()
        else:
            val = self.adc.read_adc(self.adc_channel, gain=self.adc_gain)
        self.value, self.old_value = val, self.value
        return val

    def update(self):
        value = self.read()
        old_value = self.old_value
        # Rising value
        if value > old_value:
            for x,f in self.rising_thresholds:
                if x > old_value and x < value:
                    f()
        if value < old_value:
            for x,f in self.falling_thresholds:
                if x < old_value and x > value:
                    f()

    def register_callback(self, f, threshold, threshold_type='both'):
        if threshold_type in ['rising', 'both']:
            self.rising_thresholds.append((threshold, f))
        if threshold_type in ['falling', 'both']:
            self.falling_threshold.append((threshold, f))
