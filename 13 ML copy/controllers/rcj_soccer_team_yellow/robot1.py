from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP
import math, time
from utils import *
import numpy as np
import os

class MyRobot1(RCJSoccerRobot):
    def __init__(self, robot):
        super().__init__(robot)
        self.q_table_file = os.path.join(os.getcwd(), "q_table.npy")
        self.q_table = self.load_q_table()
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.1

    def load_q_table(self):
        try:
            if os.path.exists(self.q_table_file):
                return np.load(self.q_table_file)
            else:
                return np.zeros((10, 10, 4))  # Example Q-table dimensions
        except Exception as e:
            print(f"Error loading Q-table: {e}")
            return np.zeros((10, 10, 4))

    def save_q_table(self):
        try:
            np.save(self.q_table_file, self.q_table)
            print("Q-table saved successfully.")
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def run(self):
        define_variables(self)
        try:
            while self.robot.step(TIME_STEP) != -1:
                readData(self)
                state = self.get_state()
                action = self.choose_action(state)
                reward, next_state = self.perform_action(action)
                self.update_q_table(state, action, reward, next_state)
        finally:
            self.save_q_table()

    def choose_action(self, state):
        if np.random.rand() < self.exploration_rate:
            return np.random.choice([0, 1, 2, 3])  # Random action
        return np.argmax(self.q_table[state])  # Best action from Q-table

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error

    def get_state(self):
        # Convert current position and ball position into a state
        x_state = int(self.xb * 10)
        y_state = int(self.yb * 10)
        
        # Clamp the state values to be within the bounds of the Q-table
        x_state = max(0, min(x_state, 9))
        y_state = max(0, min(y_state, 9))
        
        return (x_state, y_state)

    def perform_action(self, action):
        # Perform the chosen action and return reward and next state
        if action == 0:
            move(self, 0.4, self.yb)  # Example action
        elif action == 1:
            move(self, -0.4, self.yb)
        elif action == 2:
            motor(self, 10, -10)
        elif action == 3:
            motor(self, -10, 10)
        
        # Calculate reward based on the outcome
        reward = self.calculate_reward()
        next_state = self.get_state()
        return reward, next_state

    def calculate_reward(self):
        # Define reward calculation logic
        goal_position = 1.0  # Example goal position on the field
        distance_to_goal = abs(self.xb - goal_position)

        if self.is_ball and distance_to_goal < 0.1:
            return 10  # High reward for being close to the goal with the ball
        elif self.is_ball:
            return 1  # Reward for having the ball
        else:
            return -distance_to_goal  # Penalty based on distance from the goal