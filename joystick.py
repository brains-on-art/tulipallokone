import time
import RPi.GPIO as GPIO

# Physical pins
JOYSTICK_LEFT  = JOYSTICK_1 = 37
JOYSTICK_RIGHT = JOYSTICK_2 = 35
JOYSTICK_DOWN  = JOYSTICK_3 = 33
JOYSTICK_UP    = JOYSTICK_4 = 31

class Joystick(object):
    def __init__(self, pin_up=JOYSTICK_UP, pin_down=JOYSTICK_DOWN, pin_right=JOYSTICK_RIGHT, pin_left=JOYSTICK_LEFT):
        self.pin_up = pin_up
        self.pin_down = pin_down
        self.pin_right = pin_right
        self.pin_left = pin_left

        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BOARD)

        for pin in [pin_up, pin_down, pin_right, pin_left]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=self._pin_callback, bouncetime=100)
        self.state = [0,0]

    def _pin_callback(self, pin):
        time.sleep(0.01)
        if GPIO.input(pin):
            #print('Rising', pin)
            if pin in [self.pin_up, self.pin_down]:
                self.state[1] = 0
            elif pin in [self.pin_right, self.pin_left]:
                self.state[0] = 0
        else:
            #print('Falling', pin)
            if pin == self.pin_up:
                self.state[1] = 1
            elif pin == self.pin_down:
                self.state[1] = -1
            elif pin == self.pin_right:
                self.state[0] = 1
            elif pin == self.pin_left:
                self.state[0] = -1


if __name__ == "__main__":
    j = Joystick()

    print('Joystick Demo!\n')

    while True:
        print('Current state is:', j.state)
        time.sleep(0.1)
