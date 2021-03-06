import numpy as np
import Adafruit_PCA9685

class PanTilt(object):
    def __init__(self, pan_limits, tilt_limits, pan_channel=0, tilt_channel=1, pwm=None):
        if pwm is None:
            self.pwm = Adafruit_PCA9685.PCA9685()
            print('Assuming PWM frequency 60 Hz')
            self.pwm.set_pwm_freq(60)
        else:
            self.pwm = pwm
        
        self.pan_channel = pan_channel
        self.tilt_channel = tilt_channel
        if len(pan_limits) == 2:
            self.pan_limits = [pan_limits[0], (pan_limits[0]+pan_limits[1])/2, pan_limits[1]]
        elif len(pan_limits) == 3:
            self.pan_limits = pan_limits
        else:
            raise SyntaxError('Incorrect pan limits')
        if len(tilt_limits) == 2:
            self.tilt_limits = [tilt_limits[0], (tilt_limits[0]+tilt_limits[1])/2, tilt_limits[1]]
        elif len(tilt_limits) == 3:
            self.tilt_limits = tilt_limits
        else:
            raise SyntaxError('Incorrect tilt limits')

    def pan(self, angle=0):
        angle = np.clip(angle, -1, 1)
        pulse = int(np.interp(angle, [-1,0,1], self.pan_limits))
        self.pwm.set_pwm(self.pan_channel, 0, pulse)        

    def tilt(self, angle=0):
        angle = np.clip(angle, -1, 1)
        pulse = int(np.interp(angle, [-1,0,1], self.tilt_limits))
        self.pwm.set_pwm(self.tilt_channel, 0, pulse)
         
if __name__ == "__main__":
    # These values are specific to individual motors, change them for yours!
    p = PanTilt([140, 385, 630], [240, 450, 670])
    
    print('Pan-tilt demo!\n')

    print('Commands:')
    print('> p x (pan to x in [-1, 1])')
    print('> t x (tilt to x in [-1, 1])')

    while True:
        cmd = raw_input('> ')
        cmd, x = cmd.split()
	x = float(x)
        if cmd == 'p':
            p.pan(x)
        if cmd == 't':
            p.tilt(x)
