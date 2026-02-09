import numpy as np
from typing import Union, Callable
try:
    import pygame # necessary only for the SteeringWheelController
except ImportError:
    print('pygame is not installed, you won\'t be able to use the steering wheel.')

class KeyboardController:
    def __init__(self, world):
        self._steering = 0.
        self._throttle = 0.
        
        self.min_steering = -0.5
        self.max_steering = +0.5
        
        self.min_throttle = -1.5
        self.max_throttle = +1.5
    
        world.visualizer.win.bind("<KeyRelease-Up>", self.arrow_up_release)
        world.visualizer.win.bind("<KeyRelease-Down>", self.arrow_down_release)
        world.visualizer.win.bind("<KeyRelease-Left>", self.arrow_left_release)
        world.visualizer.win.bind("<KeyRelease-Right>", self.arrow_right_release)
        
        world.visualizer.win.bind("<KeyPress-Up>", self.arrow_up_press)
        world.visualizer.win.bind("<KeyPress-Down>", self.arrow_down_press)
        world.visualizer.win.bind("<KeyPress-Left>", self.arrow_left_press)
        world.visualizer.win.bind("<KeyPress-Right>", self.arrow_right_press)
        
        world.visualizer.win.focus_force() # very impolite... Polite version is focus_set(), but it is not always working
    
    @property
    def steering(self):
        return self._steering
    @property
    def throttle(self):
        return self._throttle
    @steering.setter
    def steering(self, val):
        self._steering = np.clip(val, self.min_steering, self.max_steering)
    @throttle.setter
    def throttle(self, val):
        self._throttle = np.clip(val, self.min_throttle, self.max_throttle)
    
    def arrow_up_release(self, event):
        self.throttle -= 1.5
    def arrow_down_release(self, event):
        self.throttle += 1.5
    def arrow_left_release(self, event):
        self.steering -= 0.5
    def arrow_right_release(self, event):
        self.steering += 0.5
        
    def arrow_up_press(self, event):
        self.throttle += 1.5
    def arrow_down_press(self, event):
        self.throttle -= 1.5
    def arrow_left_press(self, event):
        self.steering += 0.5
    def arrow_right_press(self, event):
        self.steering -= 0.5



class SteeringWheelController: # For Logitech G29 Steering Wheel
    def __init__(self, world):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
    
    @property
    def steering(self):
        events = pygame.event.get() # This is necessary
        return -self.joystick.get_axis(0) / 2.
    @property
    def throttle(self):
        events = pygame.event.get() # This is necessary
        return -self.joystick.get_axis(1)


class OpenLoopController:
    """
    A simple open-loop controller for programming car behavior.
    
    Kids define a function that returns (speed, steering) values.
    The function is called every tick with the current simulation time.
    
    Example:
        def my_control_function(t):
            # t is the current simulation time in seconds
            speed = 0.5      # throttle: -1.5 to +1.5
            steering = 0.0   # steering: -0.5 (right) to +0.5 (left)
            return speed, steering
        
        controller = OpenLoopController(my_control_function, world=w)
    
    Args:
        control_function: A function that takes time (t) and returns (speed, steering) tuple
        world: The World object (used to get current simulation time)
    """
    def __init__(self, 
                 control_function: Callable[[float], tuple] = None,
                 world = None):
        if control_function is None:
            # Default: stationary car
            control_function = lambda t: (0.0, 0.0)
        
        self._control_function = control_function
        self._world = world
        
        # Limits for safety
        self.min_steering = -0.5
        self.max_steering = +0.5
        self.min_throttle = -1.5
        self.max_throttle = +1.5
    
    @property
    def steering(self) -> float:
        """Returns the current steering angle."""
        t = self._world.t if self._world is not None else 0.0
        speed, steering = self._control_function(t)
        return np.clip(steering, self.min_steering, self.max_steering)
    
    @property
    def throttle(self) -> float:
        """Returns the current throttle (speed control)."""
        t = self._world.t if self._world is not None else 0.0
        speed, steering = self._control_function(t)
        return np.clip(speed, self.min_throttle, self.max_throttle)