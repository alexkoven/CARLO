import numpy as np
from world import World
from agents import Car, RectangleBuilding, Painting, CircleBuilding
from geometry import Point
import time
from interactive_controllers import OpenLoopController

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


def my_controller(t):
    """
    This function is called at every simulation step.
    
    Uncomment one of the examples below, or write your own!
    
    Args:
        t: Current simulation time in seconds
        
    Returns:
        speed: Throttle value (-1.5 to +1.5)
        steering: Steering angle (-0.5 to +0.5)
    """
    
    # EXAMPLE 1: Constant speed and steering (drive straight)
    # speed = 0.5
    # steering = 0.0
    
    # EXAMPLE 2: Accelerate over time
    # speed = min(0.1 * t, 1.0)  # accelerate for 10 seconds
    # steering = 0.0
    
    # EXAMPLE 3: Sinusoidal steering (weaving left and right)
    # speed = 0.5
    # steering = 0.3 * np.sin(0.5 * t)
    
    # EXAMPLE 4: Step-wise control (change at specific times)
    if t < 3:
        speed = 0.3
        steering = 0.2   # steer left
    elif t < 6:
        speed = 0.6
        steering = -0.2  # steer right
    elif t < 9:
        speed = 0.9
        steering = 0.2   # steer left again
    else:
        speed = 0.6
        steering = 0.0   # straight
    
    # EXAMPLE 5: Navigate the slalom with periodic steering
    # speed = 0.4
    # period = 5.0  # 5 seconds per weave cycle
    # steering = 0.25 * np.sin(2 * np.pi * t / period)
    
    return speed, steering

controller = OpenLoopController(my_controller, world=w)


# Run the simulation with the open-loop controller
for k in range(1200):
    c1.set_control(controller.steering, controller.throttle)
    w.tick()  # This ticks the world for one time step (dt second)
    w.render()
    time.sleep(dt/4)  # Let's watch it 4x
    
    if w.collision_exists():
        print(f'Collision at time t={w.t:.2f}s!')
        import sys
        sys.exit(0)

w.close()
