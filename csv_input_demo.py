import pandas as pd
import pulp
import matplotlib.pyplot as plt
import numpy as np

# Load CSV file
csv_path = "csv/availability_matrix.csv"
data = pd.read_csv(csv_path, header=None)

# Parameters
num_workers_needed = 3  # Number of workers needed each day

# Number of workers and days
R, C = data.shape

# Problem definition
prob = pulp.LpProblem("WorkerScheduleOptimization", pulp.LpMaximize)

# Decision variables
worker_selection = pulp.LpVariable.dicts("worker_selection", ((r, c) for r in range(R) for c in range(C)), cat="Binary")

# Objective function: Maximize the number of selected shifts (for simplicity)
prob += pulp.lpSum(worker_selection[r, c] for r in range(R) for c in range(C))

# Constraints
for c in range(C):
    # Ensure exactly 'num_workers_needed' workers are selected for each day
    prob += pulp.lpSum(worker_selection[r, c] for r in range(R)) == num_workers_needed

for r in range(R):
    for c in range(C):
        # A worker can only be selected if they are available
        if data.iloc[r, c] == 1:  # Unavailable
            prob += worker_selection[r, c] == 0

# Solve the problem
prob.solve()

# Output the result matrix
output_matrix = []
for r in range(R):
    row = []
    for c in range(C):
        if data.iloc[r, c] == 1:
            row.append('U')  # Unavailable
        elif pulp.value(worker_selection[r, c]) == 1:
            row.append('S')  # Selected for shift
        else:
            row.append('A')  # Available but not selected
    output_matrix.append(row)

# Convert output matrix to DataFrame
output_df = pd.DataFrame(output_matrix)

# Print output in a nice format
print("\nWorker Schedule:\n")
print(output_df.to_string(index=False, header=False))

# Create a table showing workers selected for each day
workers_per_day = {}
for c in range(C):
    workers_per_day[c] = [r for r in range(R) if pulp.value(worker_selection[r, c]) == 1]

print("\nWorkers Selected Per Day:\n")
for day, workers in workers_per_day.items():
    print(f"Day {day + 1}: Workers {', '.join(map(str, workers))}")

# Save output to CSV
# output_df.to_csv("/mnt/data/worker_schedule_output.csv", index=False, header=False)

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))

# Create a matrix for visualization
visual_matrix = np.zeros((R, C), dtype=int)
for r in range(R):
    for c in range(C):
        if output_df.iloc[r, c] == 'S':
            visual_matrix[r, c] = 2  # Selected
        elif output_df.iloc[r, c] == 'A':
            visual_matrix[r, c] = 1  # Available
        else:
            visual_matrix[r, c] = 0  # Unavailable

# Define a colormap
cmap = plt.get_cmap("RdYlGn", 3)
cax = ax.matshow(visual_matrix, cmap=cmap)

# Set labels and title
ax.set_xticks(np.arange(C))
ax.set_yticks(np.arange(R))
ax.set_xticklabels([f"Day {i+1}" for i in range(C)])
ax.set_yticklabels([f"Worker {i+1}" for i in range(R)])
plt.xlabel("Days")
plt.ylabel("Workers")
plt.title("Worker Schedule Visualization")

# Add colorbar
cbar = fig.colorbar(cax, ticks=[0, 1, 2])
cbar.ax.set_yticklabels(['Unavailable', 'Available', 'Selected'])

# Show the plot
plt.show()
plt.savefig("shift_matrix.png")
