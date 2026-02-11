import matplotlib.pyplot as plt

dt = 0.05
weight = 147.15 # Newtons
current_buoyancy = weight
target_buoyancy = weight + 5.0

# PID Gains (Try starting with 1.5, 0.5, 0.1)
kp, ki, kd = 1.25, 0.1, 0.0125

# State variables
integral = 0.0
prev_err = 0.0
actual_flow_rate = 0.0  # The physical speed of the pump

# Simulation lists
times, buoyancy_vals, flow_vals = [], [], []

for step in range(600):
    time = step * dt
    error = target_buoyancy - current_buoyancy
    
    # --- 1. PID Calculation (Commanded Power) ---
    integral += error * dt
    derivative = (error - prev_err) / dt
    u_commanded = (kp * error) + (ki * integral) + (kd * derivative)
    u_commanded = max(min(u_commanded, 10), -10)
    
    # --- 2. Real-World Physics Glitches ---
    
    # A. Deadzone: If u is too small, the motor doesn't budge
    u_after_deadzone = u_commanded if abs(u_commanded) > 1.2 else 0.0
    
    # B. Motor Inertia: The pump speed lags behind the command
    # This creates the "overshoot" you weren't seeing before!
    motor_inertia = 0.15 
    actual_flow_rate = (u_after_deadzone * motor_inertia) + (actual_flow_rate * (1 - motor_inertia))
    
    # --- 3. Update Buoyancy ---
    current_buoyancy += actual_flow_rate * dt
    
    # Log data
    prev_err = error
    times.append(time)
    buoyancy_vals.append(current_buoyancy)
    flow_vals.append(actual_flow_rate)

# Convert to liters per second (1 N buoyancy ≈ 0.102 L of water, ρ*g = 9810 N/m³)
flow_vals_liters = [f / 9.81 for f in flow_vals]

# Calculate cumulative water volume in tank (liters)
water_volume = []
cumulative_volume = 0.0
for flow_l_s in flow_vals_liters:
    cumulative_volume += flow_l_s * dt
    water_volume.append(cumulative_volume)

# Plotting...
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Buoyancy plot
ax1.plot(times, buoyancy_vals, label="Buoyancy (N)")
ax1.axhline(y=target_buoyancy, color='r', linestyle='--', label="Target")
ax1.set_title(f"Pump Control for Target Buoyancy\nKp={kp}, Ki={ki}, Kd={kd}")
ax1.set_ylabel("Buoyancy (N)")
ax1.legend()
ax1.grid(True)

# Flow rate and water volume plot
ax2.plot(times, flow_vals_liters, label="Flow Rate", color='green')
ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Flow Rate (L/s)", color='green')
ax2.tick_params(axis='y', labelcolor='green')
ax2.set_title("Pump Flow Rate and Water Volume")

# Add second y-axis for water volume
ax2_twin = ax2.twinx()
ax2_twin.plot(times, water_volume, label="Water Volume", color='blue', linestyle='--')
ax2_twin.set_ylabel("Water in Tank (L)", color='blue')
ax2_twin.tick_params(axis='y', labelcolor='blue')

# Combine legends
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

ax2.grid(True)

plt.tight_layout()
plt.savefig("buoyancy_plot.png")

# ====================================================================
# SIMULATION 2: Time-Varying Target (Realistic Depth Profile)
# ====================================================================

# Reset state variables
current_buoyancy_2 = weight
integral_2 = 0.0
prev_err_2 = 0.0
actual_flow_rate_2 = 0.0

# Simulation lists
times_2, buoyancy_vals_2, flow_vals_2, target_vals_2 = [], [], [], []

def get_target_buoyancy(t):
    """Realistic submarine depth profile:
    0-5s: Descend (increase buoyancy to +10N)
    5-15s: Hold depth
    15-20s: Ascend to mid-depth (+5N)
    20-30s: Hold at mid-depth
    """
    if t < 5:
        # Gradual descent
        return weight + (10.0 * t / 5.0)
    elif t < 15:
        # Hold at depth
        return weight + 10.0
    elif t < 20:
        # Gradual ascent to mid-depth
        progress = (t - 15) / 5.0
        return weight + 10.0 - (5.0 * progress)
    else:
        # Hold at mid-depth
        return weight + 5.0

for step in range(600):
    time = step * dt
    target = get_target_buoyancy(time)
    error = target - current_buoyancy_2
    
    # --- 1. PID Calculation ---
    integral_2 += error * dt
    derivative = (error - prev_err_2) / dt
    u_commanded = (kp * error) + (ki * integral_2) + (kd * derivative)
    u_commanded = max(min(u_commanded, 10), -10)
    
    # --- 2. Real-World Physics ---
    u_after_deadzone = u_commanded if abs(u_commanded) > 1.2 else 0.0
    motor_inertia = 0.15 
    actual_flow_rate_2 = (u_after_deadzone * motor_inertia) + (actual_flow_rate_2 * (1 - motor_inertia))
    
    # --- 3. Update Buoyancy ---
    current_buoyancy_2 += actual_flow_rate_2 * dt
    
    # Log data
    prev_err_2 = error
    times_2.append(time)
    buoyancy_vals_2.append(current_buoyancy_2)
    flow_vals_2.append(actual_flow_rate_2)
    target_vals_2.append(target)

# Convert to liters per second
flow_vals_liters_2 = [f / 9.81 for f in flow_vals_2]

# Calculate cumulative water volume
water_volume_2 = []
cumulative_volume_2 = 0.0
for flow_l_s in flow_vals_liters_2:
    cumulative_volume_2 += flow_l_s * dt
    water_volume_2.append(cumulative_volume_2)

# Plotting Simulation 2
fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Buoyancy plot
ax1.plot(times_2, buoyancy_vals_2, label="Actual Buoyancy (N)", linewidth=2)
ax1.plot(times_2, target_vals_2, 'r--', label="Target Buoyancy (N)", linewidth=2)
ax1.set_title(f"Pump Control with Time-Varying Target Buoyancy\nKp={kp}, Ki={ki}, Kd={kd}")
ax1.set_ylabel("Buoyancy (N)")
ax1.legend()
ax1.grid(True)

# Flow rate and water volume plot
ax2.plot(times_2, flow_vals_liters_2, label="Flow Rate", color='green')
ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Flow Rate (L/s)", color='green')
ax2.tick_params(axis='y', labelcolor='green')
ax2.set_title("Pump Flow Rate and Water Volume")

# Add second y-axis for water volume
ax2_twin = ax2.twinx()
ax2_twin.plot(times_2, water_volume_2, label="Water Volume", color='blue', linestyle='--')
ax2_twin.set_ylabel("Water in Tank (L)", color='blue')
ax2_twin.tick_params(axis='y', labelcolor='blue')

# Combine legends
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

ax2.grid(True)

plt.tight_layout()
plt.savefig("buoyancy_plot_varying.png")

print("Simulation complete!")
print(f"Static target plot saved to: buoyancy_plot.png")
print(f"Time-varying target plot saved to: buoyancy_plot_varying.png")