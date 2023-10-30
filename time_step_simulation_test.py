import pandas as pd

# Read the TSV (Tab Separated Values) data into a DataFrame
path = "/home/dcope/LABx_Project/Radarsimpy_simulation/data/04_CRW2L_MC_V1_tx1.tsv"
df = pd.read_csv(path, sep='\t')

# Initialize an empty list for mocap data
mocap_data = []

# Prefixes from your CSV columns (assuming all body parts have both position and velocity data)
prefixes = ['Wrist_R', 'Elbow_R', 'Shoulder_R', 'Wrist_L', 'Elbow_L', 'Shoulder_L', 'Upper_Back', 'Lower_Back', 'Chest', 'Belly', 
            'Hip_R_Ant', 'Hip_L_Ant', 'Hip_R_Post', 'Hip_L_Post', 'Knee_R', 'Knee_L', 'Ankle_R', 'Ankle_L']

# Iterate through each row in the DataFrame
for _, row in df.iterrows():
    timestep_data = []
    for prefix in prefixes:
        location = [row[f'{prefix}_pos_X'], row[f'{prefix}_pos_Y'], row[f'{prefix}_pos_Z']]
        speed = [row[f'{prefix}_vel_X'], row[f'{prefix}_vel_Y'], row[f'{prefix}_vel_Z']]
        
        # Assuming rcs is not present in your data and is a constant value (10 for the example). Adjust as needed.
        rcs = 1  # Adjust this value if needed
        timestep_data.append({'location': location, 'speed': speed, 'rcs': rcs})
    
    mocap_data.append(timestep_data)

# # To verify, print the first two timesteps
# for i in range(2):
#     print(mocap_data[i])
#     print("\n")


import math

# Define the rotation matrix for 180 degrees about the Z axis
def rotate_180(x, y):
    # For 180 degrees rotation, the new coordinates are:
    x_new = -x
    y_new = y
    return x_new, y_new

# Adjust the data
for timestep in mocap_data:
    for entry in timestep:
        # Translation: Shift in the positive x direction by 5 units
        entry['location'][0] += 5
        
        # Rotation: 180 degrees about the Z axis
        entry['location'][0], entry['location'][1] = rotate_180(round(entry['location'][0], 5), round(entry['location'][1], 5))
        entry['speed'][0], entry['speed'][1] = rotate_180(round(entry['speed'][0], 5), round(entry['speed'][1], 5))

# # To verify, print the first two timesteps
# for i in range(2):
#     print(mocap_data[i])
#     print("\n")
