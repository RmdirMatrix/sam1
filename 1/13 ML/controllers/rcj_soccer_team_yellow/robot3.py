from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP
import math, time
from utils import *

class MyRobot3(RCJSoccerRobot):
    def run(self):
        define_variables(self)
        step = 0
        while self.robot.step(TIME_STEP) != -1:
            readData(self)
            manualControl(self)
            input_data = {
                'xr': self.xr,
                'yr': self.yr,
                'xb': self.xb,
                'yb': self.yb,
                'heading': self.heading,
                'step': step,
            }
            output_data = {
                'vl': self.vl,
                'vr': self.vr,
            }
            step += 1