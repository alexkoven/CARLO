import numpy as np
from world import World
from agents import Car, RingBuilding, CircleBuilding, Painting, Pedestrian
from geometry import Point
import time
from tkinter import *

# Choose your control mode:
# 'keyboard' - use arrow keys to control the car
# 'openloop' - use a programmed speed and steering function
# 'auto' - use the built-in automatic controller
control_mode = 'openloop'  # Options: 'keyboard', 'openloop', 'auto'

dt = 0.1 # time steps in terms of seconds. In other words, 1/dt is the FPS.
world_width = 120 # in meters
world_height = 120
inner_building_radius = 30
num_lanes = 2
lane_marker_width = 0.5
num_of_lane_markers = 50
lane_width = 3.5

w = World(dt, width = world_width, height = world_height, ppm = 6) # The world is 120 meters by 120 meters. ppm is the pixels per meter.



# Let's add some sidewalks and RectangleBuildings.
# A Painting object is a rectangle that the vehicles cannot collide with. So we use them for the sidewalks / zebra crossings / or creating lanes.
# A CircleBuilding or RingBuilding object is also static -- they do not move. But as opposed to Painting, they can be collided with.

# To create a circular road, we will add a CircleBuilding and then a RingBuilding around it
cb = CircleBuilding(Point(world_width/2, world_height/2), inner_building_radius, 'gray80')
w.add(cb)
rb = RingBuilding(Point(world_width/2, world_height/2), inner_building_radius + num_lanes * lane_width + (num_lanes - 1) * lane_marker_width, 1+np.sqrt((world_width/2)**2 + (world_height/2)**2), 'gray80')
w.add(rb)

# Let's also add some lane markers on the ground. This is just decorative. Because, why not.
for lane_no in range(num_lanes - 1):
    lane_markers_radius = inner_building_radius + (lane_no + 1) * lane_width + (lane_no + 0.5) * lane_marker_width
    lane_marker_height = np.sqrt(2*(lane_markers_radius**2)*(1-np.cos((2*np.pi)/(2*num_of_lane_markers)))) # approximate the circle with a polygon and then use cosine theorem
    for theta in np.arange(0, 2*np.pi, 2*np.pi / num_of_lane_markers):
        dx = lane_markers_radius * np.cos(theta)
        dy = lane_markers_radius * np.sin(theta)
        w.add(Painting(Point(world_width/2 + dx, world_height/2 + dy), Point(lane_marker_width, lane_marker_height), 'white', heading = theta))
    

# A Car object is a dynamic object -- it can move. We construct it using its center location and heading angle.
c1 = Car(Point(91.75,60), np.pi/2)
c1.max_speed = 30.0 # let's say the maximum is 30 m/s (108 km/h)
c1.velocity = Point(0, 0)  # Start stationary
w.add(c1)

w.render() # This visualizes the world we just constructed.



if control_mode == 'openloop':
    # OPEN-LOOP CONTROL: Modify the my_controller function below!
    from interactive_controllers import OpenLoopController
    
    def my_controller(t):
        """
        This function is called at every simulation step.
        
        Args:
            t: Current simulation time in seconds
            
        Returns:
            speed: Throttle value (-1.5 to +1.5)
                   Positive = accelerate, Negative = brake/reverse
            steering: Steering angle (-0.5 to +0.5)
                      Positive = left, Negative = right
        """
        # Example 1: Constant speed and turn (for circular track)
        # Note: Negative steering = right turn, needed for counterclockwise circle
        speed = 0.6
        steering = 0.1  # constant right turn
        
        # Example 2: Accelerate while turning
        # speed = min(0.05 * t, 0.5)  # accelerate gradually up to 0.5
        # steering = -0.15
        
        # Example 3: Change speed on different parts of track
        # # Use modulo to repeat pattern every ~40 seconds (one lap)
        # lap_time = t % 40
        # if lap_time < 10:
        #     speed = 0.5      # fast on first quarter
        #     steering = -0.15
        # elif lap_time < 20:
        #     speed = 0.3      # slow on second quarter
        #     steering = -0.15
        # elif lap_time < 30:
        #     speed = 0.5      # fast on third quarter
        #     steering = -0.15
        # else:
        #     speed = 0.3      # slow on fourth quarter
        #     steering = -0.15
        
        return speed, steering
    
    controller = OpenLoopController(my_controller, world=w)
    
    for k in range(3600):
        c1.set_control(controller.steering, controller.throttle)
        w.tick()
        w.render()
        time.sleep(dt/4)
        
        if w.collision_exists():
            print(f'Collision at time t={w.t:.2f}s!')
            import sys
            sys.exit(0)
    w.close()

elif control_mode == 'auto':
    # AUTOMATIC CONTROL: Lane-keeping policy for circular road
    desired_lane = 1
    for k in range(600):
        lp = 0.
        if c1.distanceTo(cb) < desired_lane*(lane_width + lane_marker_width) + 0.2:
            lp += 0.
        elif c1.distanceTo(rb) < (num_lanes - desired_lane - 1)*(lane_width + lane_marker_width) + 0.3:
            lp += 1.
        
        v = c1.center - cb.center
        v = np.mod(np.arctan2(v.y, v.x) + np.pi/2, 2*np.pi)
        if c1.heading < v:
            lp += 0.7
        else:
            lp += 0.
        
        if np.random.rand() < lp: c1.set_control(0.2, 0.1)
        else: c1.set_control(-0.1, 0.1)
        
        w.tick()
        w.render()
        time.sleep(dt/4)

        if w.collision_exists():
            print('Collision exists somewhere...')
    w.close()

else:  # control_mode == 'keyboard'
    # KEYBOARD CONTROL: Use arrow keys
    from interactive_controllers import KeyboardController
    c1.set_control(0., 0.)
    controller = KeyboardController(w)
    
    for k in range(3600):
        c1.set_control(controller.steering, controller.throttle)
        w.tick()
        w.render()
        time.sleep(dt/4)
        
        if w.collision_exists():
            print(f'Collision at time t={w.t:.2f}s!')
            import sys
            sys.exit(0)
    w.close()