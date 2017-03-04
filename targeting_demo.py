import time
import numpy as np
from joystick import Joystick
from pan_tilt import PanTilt



if __name__ == "__main__":
    j = Joystick()
    # These values are specific to individual motors, change them for yours!
    p = PanTilt([140, 385, 630], [240, 450, 670])
    
    print('Targeting Demo!\n')
    print('Use joystick to move pan-tilt')

    X_SPEED = 0.01
    Y_SPEED = -0.01 # Invert Y

    x,y = 0,0
    p.pan(x)
    p.tilt(y)

    while True:
        x_ctrl, y_ctrl = j.state
        
        x = np.clip(x+X_SPEED*x_ctrl, -1, 1)            
        y = np.clip(y+Y_SPEED*y_ctrl, -1, 1)
        
        p.pan(x)
        p.tilt(y)

        time.sleep(0.01)
