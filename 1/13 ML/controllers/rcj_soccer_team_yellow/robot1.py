from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP
import math, time
from utils import *

class MyRobot1(RCJSoccerRobot):
    def GoalKeeperAI(self):
        if self.yb < -0.5 and (self.xb > 0.3 or self.yb < -0.3):
            if self.xb > 0:
                move(self, 0.4, self.yb)
            else:
                move(self, -0.4, self.yb)
        elif self.yr > -0.5 or self.yr < -0.55:
            move(self, clamp(self.xb, -0.4, 0.4), -0.55)
        else:
            if self.heading > 95: 
                motor(self, -10, 10)
            elif self.heading < 85:
                motor(self, 10, -10)
            else:
                if not self.is_ball: self.xb = 0
                
                if clamp(self.xb, -0.4, 0.4) > self.xr:
                    motor(self, -10, -10)
                else:
                    motor(self, 10, 10)
    def run(self):
        define_variables(self)
        while self.robot.step(TIME_STEP) != -1:
            readData(self)
            # print(self.sonar['front']/1000)
            # if self.manual_control:
            #     manualControl(self)
            # else:
            #     self.GoalKeeperAI()