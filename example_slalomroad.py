import numpy as np
from world import World
from agents import Car, RectangleBuilding, Painting, CircleBuilding
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
road_width = 25  # total width of the road for the slalom course
cone_radius = 1.5  # radius of slalom cones

w = World(dt, width=world_width, height=world_height, ppm=6)  # The world is 120 meters by 120 meters. ppm is the pixels per meter.

# Create a wide straight road with boundaries for the slalom course
# Left sidewalk and building
w.add(Painting(Point(world_width/2 - road_width/2 - 5, world_height/2), Point(10, world_height), 'gray80'))
w.add(RectangleBuilding(Point(world_width/2 - road_width/2 - 5, world_height/2), Point(8, world_height - 4)))

# Right sidewalk and building
w.add(Painting(Point(world_width/2 + road_width/2 + 5, world_height/2), Point(10, world_height), 'gray80'))
w.add(RectangleBuilding(Point(world_width/2 + road_width/2 + 5, world_height/2), Point(8, world_height - 4)))

# Add edge lane markers (solid lines on the sides of the road)
lane_marker_length = 3.0
y_start = 5
y_end = world_height - 5

# Left edge
for y in np.arange(y_start, y_end, lane_marker_length):
    w.add(Painting(Point(world_width/2 - road_width/2 + 1, y + lane_marker_length/2), 
                   Point(0.5, lane_marker_length), 
                   'white', 
                   heading=np.pi/2))

# Right edge
for y in np.arange(y_start, y_end, lane_marker_length):
    w.add(Painting(Point(world_width/2 + road_width/2 - 1, y + lane_marker_length/2), 
                   Point(0.5, lane_marker_length), 
                   'white', 
                   heading=np.pi/2))

# Create slalom cones in a straight line directly in front of the car
# Car starts at y=10, so we space cones evenly from y=30 to y=105
num_cones = 4
first_cone_y = 30  # start position of first cone (20 meters ahead of car)
last_cone_y = 105  # end position of last cone
cone_spacing = (last_cone_y - first_cone_y) / (num_cones - 1)  # evenly distribute cones

for i in range(num_cones):
    y_pos = first_cone_y + i * cone_spacing
    # All cones at the center x position (directly in front of car)
    x_pos = world_width/2
    
    # Add a CircleBuilding as a cone (colored orange for visibility)
    cone = CircleBuilding(Point(x_pos, y_pos), cone_radius, 'orange')
    w.add(cone)

# A Car object is a dynamic object -- it can move. We construct it using its center location and heading angle.
c1 = Car(Point(world_width/2, 10), np.pi/2)
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
        # Example 1: Weave left and right with sinusoidal steering
        speed = 0.4
        period = 5.0  # 5 seconds per weave cycle
        steering = 0.25 * np.sin(2 * np.pi * t / period)
        
        # Example 2: Step-wise steering (turn at specific times)
        # speed = 0.4
        # if t < 3:
        #     steering = 0.2   # turn left
        # elif t < 6:
        #     steering = -0.2  # turn right
        # elif t < 9:
        #     steering = 0.2   # turn left
        # else:
        #     steering = -0.2  # turn right
        
        # Example 3: Gradually increase turning
        # speed = 0.4
        # steering = min(0.05 * t, 0.3)  # gradually turn more left
        
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
    # AUTOMATIC CONTROL: Simple slalom policy
    for k in range(1000):
        # Determine which cone is closest ahead
        y_pos = c1.center.y
        cone_index = int((y_pos - first_cone_y) / cone_spacing)
        
        if cone_index < num_cones:
            # Alternate between steering left and right to avoid center cones
            if cone_index % 2 == 0:
                target_x = world_width/2 + 4
            else:
                target_x = world_width/2 - 4
            
            # Simple proportional steering control
            x_error = target_x - c1.center.x
            steering = np.clip(x_error * 0.15, -0.5, 0.5)
            c1.set_control(steering, 0.25)
        else:
            c1.set_control(0, 0.25)
        
        w.tick()
        w.render()
        time.sleep(dt/4)

        if w.collision_exists():
            print('Collision with cone!')
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
