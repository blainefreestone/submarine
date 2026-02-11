import matplotlib.pyplot as plt
import numpy as np

class PID:
    def __init__(self, kp, ki, kd, limit, windup_limit=5):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.limit = limit
        self.windup_limit = windup_limit
        self.integral = 0
        self.prev_error = 0

    def compute(self, target, current, dt):
        error = target - current
        self.integral = np.clip(self.integral + error * dt, -self.windup_limit, self.windup_limit)
        derivative = (error - self.prev_error) / dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return np.clip(output, -self.limit, self.limit)

class BallastSystem:
    def __init__(self, initial_buoyancy, dt):
        self.buoyancy = initial_buoyancy
        self.actual_flow_rate = 0.0
        self.dt = dt
        # Physics Parameters
        self.deadzone = 1.2
        self.motor_inertia = 0.15
        self.max_pump_power = 10.0
        self.u_after_deadzone = 0.0

    def update(self, pump_command):
        # Apply Deadzone
        self.u_after_deadzone = pump_command if abs(pump_command) > self.deadzone else 0.0
        # Apply Motor Inertia
        self.actual_flow_rate = (self.u_after_deadzone * self.motor_inertia) + (self.actual_flow_rate * (1 - self.motor_inertia))
        # Update physical buoyancy
        self.buoyancy += self.actual_flow_rate * self.dt
        return self.buoyancy

class Submarine:
    def __init__(self, mass, drag_coeff):
        self.mass = mass
        self.drag_coeff = drag_coeff
        self.weight = mass * 9.81
        self.depth = 0.0
        self.velocity = 0.0

    def update(self, current_buoyancy, dt):
        drag_force = self.drag_coeff * self.velocity
        # Net force = Gravity - Buoyancy - Drag
        net_force = self.weight - current_buoyancy - drag_force
        
        acceleration = net_force / self.mass
        self.velocity += acceleration * dt
        self.depth += self.velocity * dt
        return self.depth

# --- Simulation Setup ---
dt = 0.05
sim_time = 60
steps = int(sim_time / dt)

sub = Submarine(mass=15.0, drag_coeff=0.5)
ballast = BallastSystem(initial_buoyancy=sub.weight, dt=dt)

# Controller Tuning
# Outer Loop: Depth -> Target Buoyancy Offset
depth_pid = PID(kp=0.06, ki=0.1, kd=7.5, limit=20.0) 
# Inner Loop: Buoyancy Error -> Pump Power
buoyancy_pid = PID(kp=1.25, ki=0.1025, kd=0.0125, limit=ballast.max_pump_power)

# Data Tracking
history = {'time': [], 'depth': [], 'target_depth': [], 'buoyancy': [], 'target_buoyancy': [], 'pump_cmd': [], 'actual_flow_rate': [], 'pump_active': []}

target_depth = 10.0

for i in range(steps):
    t = i * dt
    
    # 1. OUTER LOOP: Determine needed buoyancy to reach depth
    # The PID output is the "Desired Buoyancy Offset" from neutral
    buoyancy_offset_cmd = depth_pid.compute(target_depth, sub.depth, dt)
    target_buoyancy = sub.weight - buoyancy_offset_cmd
    
    # 2. INNER LOOP: Command the pump to hit that buoyancy
    pump_cmd = buoyancy_pid.compute(target_buoyancy, ballast.buoyancy, dt)
    
    # 3. PHYSICS: Update systems
    current_b = ballast.update(pump_cmd)
    current_d = sub.update(current_b, dt)
    
    # Log
    history['time'].append(t)
    history['depth'].append(current_d)
    history['target_depth'].append(target_depth)
    history['buoyancy'].append(current_b)
    history['target_buoyancy'].append(target_buoyancy)
    history['pump_cmd'].append(pump_cmd)
    history['actual_flow_rate'].append(ballast.actual_flow_rate)
    history['pump_active'].append(ballast.u_after_deadzone)

# --- Plotting ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

ax1.plot(history['time'], history['depth'], label="Current Depth")
ax1.axhline(y=target_depth, color='r', linestyle='--', label="Target Depth")
ax1.set_ylabel("Depth (m)")
ax1.invert_yaxis() # Depth is usually shown downward
ax1.legend()
ax1.grid(True)

ax2.plot(history['time'], history['buoyancy'], label="Actual Buoyancy")
ax2.plot(history['time'], history['target_buoyancy'], 'g--', label="Target Buoyancy (from Depth PID)")
ax2.set_ylabel("Buoyancy (N)")
ax2.legend()
ax2.grid(True)

ax3.plot(history['time'], history['pump_active'], label="Pump Command (After Deadzone)", color='purple', linewidth=2)
ax3.axhline(y=0, color='red', linestyle='--', linewidth=1, label="Damped (Off)")
ax3.set_ylabel("Pump Command (N/s)")
ax3.set_xlabel("Time (s)")
ax3.legend()
ax3.grid(True)

plt.tight_layout()
plt.savefig("submarine_depth_control_short.png")