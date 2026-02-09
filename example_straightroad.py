import numpy as np
from world import World
from agents import Car, RectangleBuilding, Painting
from geometry import Point
import time

# Choose your control mode:
# 'keyboard' - use arrow keys to control the car
# 'openloop' - use a programmed speed and steering function
# 'auto' - use the built-in automatic controller
control_mode = 'openloop'  # Options: 'keyboard', 'openloop', 'auto'

dt = 0.1  # time steps in terms of seconds. In other words, 1/dt is the FPS.
world_width = 120  # in meters
world_height = 120
road_width = 20  # total width of the road
lane_width = 3.5
num_lanes = 2
lane_marker_width = 0.5
num_of_lane_markers = 20

w = World(dt, width=world_width, height=world_height, ppm=6)  # The world is 120 meters by 120 meters. ppm is the pixels per meter.

# Create a straight vertical road in the center of the world
# Left sidewalk and building
w.add(Painting(Point(world_width/2 - road_width/2 - 5, world_height/2), Point(10, world_height), 'gray80'))
w.add(RectangleBuilding(Point(world_width/2 - road_width/2 - 5, world_height/2), Point(8, world_height - 4)))

# Right sidewalk and building
w.add(Painting(Point(world_width/2 + road_width/2 + 5, world_height/2), Point(10, world_height), 'gray80'))
w.add(RectangleBuilding(Point(world_width/2 + road_width/2 + 5, world_height/2), Point(8, world_height - 4)))

# Add lane markers in the center of the road (dashed line pattern)
lane_marker_length = 3.0
lane_marker_spacing = 5.0
y_start = 5
y_end = world_height - 5

for y in np.arange(y_start, y_end, lane_marker_length + lane_marker_spacing):
    w.add(Painting(Point(world_width/2, y + lane_marker_length/2), 
                   Point(lane_marker_width, lane_marker_length), 
                   'white', 
                   heading=np.pi/2))

# Add edge lane markers (solid lines on the sides of the road)
# Left edge
for y in np.arange(y_start, y_end, lane_marker_length):
    w.add(Painting(Point(world_width/2 - road_width/2 + 1, y + lane_marker_length/2), 
                   Point(lane_marker_width, lane_marker_length), 
                   'white', 
                   heading=np.pi/2))

# Right edge
for y in np.arange(y_start, y_end, lane_marker_length):
    w.add(Painting(Point(world_width/2 + road_width/2 - 1, y + lane_marker_length/2), 
                   Point(lane_marker_width, lane_marker_length), 
                   'white', 
                   heading=np.pi/2))

# A Car object is a dynamic object -- it can move. We construct it using its center location and heading angle.
c1 = Car(Point(world_width/2 - lane_width/2, 20), np.pi/2)
c1.max_speed = 30.0  # let's say the maximum is 30 m/s (108 km/h)
c1.velocity = Point(0, 0)  # Start stationary
w.add(c1)

w.render()  # This visualizes the world we just constructed.


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
        # Example 1: Drive straight at constant speed
        speed = 0.5
        steering = 0.0
        
        # Example 2: Accelerate over time
        # speed = min(0.1 * t, 1.0)  # accelerate for 10 seconds
        # steering = 0.0
        
        # Example 3: Weave left and right slightly
        # speed = 0.5
        # steering = 0.05 * np.sin(t)
        
        # Example 4: Change behavior at different times
        # if t < 5:
        #     speed = 0.3
        #     steering = 0.0
        # elif t < 10:
        #     speed = 0.6
        #     steering = 0.1  # slight left turn
        # else:
        #     speed = 0.9
        #     steering = 0.0
        
        return speed, steering+0.1
    
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
    # AUTOMATIC CONTROL: Simple policy - just drive straight
    for k in range(800):
        c1.set_control(0, 0.3)  # No steering, constant throttle
        
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
