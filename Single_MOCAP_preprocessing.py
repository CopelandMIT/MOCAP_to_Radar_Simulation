import pandas as pd
import numpy as np
import re

# File paths
vel_filepath = 'data/04_CRW2L_MC_V1_vel.tsv'
pos_filepath = 'data/04_CRW2L_MC_V1_pos.tsv'
combined_filepath = 'data/04_CRW2L_MC_V1.tsv'
yoga_pose_filepath = 'data/pose_vectors.csv'

# Load the files
vel_data = pd.read_csv(vel_filepath, delimiter='\t', skiprows=5, header=None)
pos_data = pd.read_csv(pos_filepath, delimiter='\t', skiprows=5, header=None)
yoga_pose_data = pd.read_csv(yoga_pose_filepath)

# Extract the identifier from the filename
identifier = re.search(r'([A-Z0-9]{5})', vel_filepath).group(1)

# Select "Time" and the specific column based on the identifier from yoga_pose_data
selected_columns = ['Time', identifier] if identifier in yoga_pose_data.columns else ['Time']
yoga_pose_data = yoga_pose_data[selected_columns]

# Rename the identifier column to "Pose"
yoga_pose_data.rename(columns={identifier: 'Pose'}, inplace=True)

# Drop the cell at position (0,0) and shift data for vel_data
vel_data.iloc[0, :-1] = vel_data.iloc[0, 1:].values
vel_data.iloc[0, -1] = np.nan
vel_data = vel_data.drop(columns=vel_data.columns[-1])

# Set headers for vel_data and drop the shifted row
vel_data.columns = vel_data.iloc[0]
vel_data = vel_data.drop(0)

# Drop the cell at position (0,0) and shift data for pos_data
pos_data.iloc[0, :-1] = pos_data.iloc[0, 1:].values
pos_data.iloc[0, -1] = np.nan
pos_data = pos_data.drop(columns=pos_data.columns[-1])

# Set headers for pos_data and drop the shifted row
pos_data.columns = pos_data.iloc[0]
pos_data = pos_data.drop(0)

# Check if the number of rows are the same for both datasets
if len(vel_data) != len(pos_data):
    raise ValueError("The number of rows in the velocity and position data are not the same.")

# Add a time vector based on the given frequency
frequency = 100  # 100Hz
time_vector = np.around(np.arange(0, len(vel_data) * 0.01, 0.01), 2)  # Given 100Hz, time step is 0.01 seconds

# Insert the time vector into the beginning of velocity dataframe
vel_data.insert(0, 'Time', time_vector)

# Combine the velocity and position datasets
combined_data = pd.concat([vel_data, pos_data], axis=1)

# Merge combined_data with yoga_pose_data based on "Time"
combined_data = combined_data.merge(yoga_pose_data, on='Time', how='left')

# Convert units for all columns except for 'Time' and 'Pose'
for col in combined_data.columns:
    if col not in ['Time', 'Pose']:
        combined_data[col] = pd.to_numeric(combined_data[col], errors='coerce')
        combined_data[col] = (combined_data[col]/ 1000).round(5)


# Reorder the columns to have "Pose" as the second column
cols = combined_data.columns.tolist()
cols.insert(1, cols.pop(cols.index('Pose')))
combined_data = combined_data[cols]

# Save the combined data to different segments based on time intervals
time_segments = [(8.47, 11.46, '_tx1'), 
                 (16.47, 19.46, '_tx2'), 
                 (24.47, 27.46, '_tx3')]

for start_time, end_time, suffix in time_segments:
    segment_data = combined_data[(combined_data['Time'] >= start_time) & (combined_data['Time'] <= end_time)]
    segment_filepath = combined_filepath.replace('.tsv', f'{suffix}.tsv')
    segment_data.to_csv(segment_filepath, sep='\t', index=False)
    print(f"Segmented data saved to {segment_filepath}")
