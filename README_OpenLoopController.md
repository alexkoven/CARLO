# OpenLoopController Guide

The `OpenLoopController` allows you to program your car's behavior by writing a simple function that returns **speed** and **steering** values.

## Quick Start

### 1. The Control Mode

All `example_*.py` files default to `'openloop'` mode. You can change this at the top of the file:

```python
control_mode = 'openloop'  # Options: 'keyboard', 'openloop', 'auto'
```

### 2. Modify the Controller Function

Find the `my_controller(t)` function in the example file and modify it:

```python
def my_controller(t):
    """
    This function is called at every simulation step.
    
    Args:
        t: Current simulation time in seconds
        
    Returns:
        speed: How fast to go (-1.5 to +1.5)
        steering: Which direction to turn (-0.5 to +0.5)
    """
    speed = 0.5      # Set your speed here
    steering = 0.0   # Set your steering here
    
    return speed, steering
```

That's it! Just modify the `speed` and `steering` variables.

## Examples

### Example 1: Drive Straight at Constant Speed

```python
def my_controller(t):
    speed = 0.5      # constant speed
    steering = 0.0   # no turning
    return speed, steering
```

### Example 2: Accelerate Over Time

```python
def my_controller(t):
    speed = min(0.1 * t, 1.0)  # accelerate for 10 seconds
    steering = 0.0
    return speed, steering
```

### Example 3: Change Behavior at Different Times

```python
def my_controller(t):
    if t < 5:
        speed = 0.3
        steering = 0.0     # drive straight slowly
    elif t < 10:
        speed = 0.5
        steering = 0.2     # speed up and turn left
    else:
        speed = 0.7
        steering = 0.0     # go fast straight
    
    return speed, steering
```

### Example 4: Weave Left and Right

```python
def my_controller(t):
    speed = 0.4
    period = 5.0  # 5 seconds per weave
    steering = 0.25 * np.sin(2 * np.pi * t / period)
    return speed, steering
```

### Example 5: React to Current Time

```python
def my_controller(t):
    # Use modulo (%) to repeat patterns
    lap_time = t % 20  # repeat every 20 seconds
    
    if lap_time < 5:
        speed = 0.8      # fast
        steering = 0.0
    elif lap_time < 10:
        speed = 0.3      # slow down
        steering = 0.2   # turn left
    elif lap_time < 15:
        speed = 0.8      # speed up again
        steering = 0.0
    else:
        speed = 0.3      # slow down
        steering = -0.2  # turn right
    
    return speed, steering
```

## Parameter Ranges

- **Steering**: 
  - `-0.5` to `+0.5`
  - Negative = turn right
  - Positive = turn left
  - Zero = straight

- **Speed (throttle)**: 
  - `-1.5` to `+1.5`
  - Negative = brake or reverse
  - Positive = accelerate forward
  - Zero = no throttle (car will slow down due to friction)

## Tips for Success

1. **Start simple**: Begin with constant speed and steering
2. **Small steering values**: Use small numbers like 0.1 or 0.2 for smooth turns
3. **Test often**: Run your code after each change to see what happens
4. **Use time wisely**: The variable `t` tells you how many seconds have passed
5. **Use print()**: Add `print(t, speed, steering)` to debug your function

## Available Environments

- **`example_straightroad.py`** - Practice maintaining speed and staying in lane
- **`example_slalomroad.py`** - Navigate around obstacles in a straight line
- **`example_circularroad.py`** - Drive around a circular track (use constant right turn!)
- **`example_intersection.py`** - Complex urban environment

## How to Run

```bash
# Make sure you're in the correct environment
conda activate driving_sim

# Run any example
python example_straightroad.py
python example_slalomroad.py
python example_circularroad.py
```

Have fun programming your car!
