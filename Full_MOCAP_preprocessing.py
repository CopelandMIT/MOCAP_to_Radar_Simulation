import pandas as pd
import numpy as np
import re
import os

Pose_Labels = ['CRW2R','CRW2L', 'CT2CW', 'FF2MN', 'MNTRR', 'MNTRL']
Participant_Labels = ['01','02', '03', '04', '09', '10', '12', '13', '14', '15', '16', '18', '22', '24']
Participant_Labels = ['01']
yoga_pose_filepath = 'data/pose_vectors.csv'
yoga_pose_data = pd.read_csv(yoga_pose_filepath)
print(yoga_pose_data)
base_dir = '/media/dcope/DC_LaCie/Yoga_Study_MOCAP_Data'

for participant in Participant_Labels:
    participant_dir = os.path.join(base_dir, participant, 'tsv')
    if os.path.exists(participant_dir):
        for file in os.listdir(participant_dir):
            if any(pose in file for pose in Pose_Labels) and '_vel.tsv' in file:
                vel_filepath = os.path.join(participant_dir, file)
                pos_filepath = vel_filepath.replace('_vel.tsv', '_pos.tsv')
                
                if os.path.exists(pos_filepath):
                    # Load the files
                    vel_data = pd.read_csv(vel_filepath, delimiter='\t', skiprows=5, header=None)
                    pos_data = pd.read_csv(pos_filepath, delimiter='\t', skiprows=5, header=None)
                    
                    # Extract the identifier from the filename based on Pose_Labels
                    identifier = None
                    for pose in Pose_Labels:
                        if pose in vel_filepath:
                            identifier = pose
                            break

                    if not identifier:
                        raise ValueError(f"No pose label found in the filename: {vel_filepath}")

                    # Create a copy of the yoga_pose_data for this iteration
                    yoga_pose_data_copy = yoga_pose_data.copy()

                    # Select "Time" and the specific column based on the identifier from yoga_pose_data
                    selected_columns = ['Time', identifier] if identifier in yoga_pose_data_copy.columns else ['Time']
                    yoga_pose_data_copy = yoga_pose_data_copy[selected_columns]

                    # Rename the identifier column to "Pose"
                    yoga_pose_data_copy.rename(columns={identifier: 'Pose'}, inplace=True)

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

                    # Merge combined_data with yoga_pose_data_copy based on "Time"
                    combined_data = combined_data.merge(yoga_pose_data_copy[['Time', 'Pose']], on='Time', how='left')


                    # Convert units for all columns except for 'Time' and 'Pose'
                    for col in combined_data.columns:
                        if col not in ['Time', 'Pose']:
                            combined_data[col] = pd.to_numeric(combined_data[col], errors='coerce')
                            combined_data[col] = (combined_data[col]/ 1000).round(5)

                    print(combined_data)
                    # Reorder the columns to have "Pose" as the second column
                    cols = combined_data.columns.tolist()
                    if 'Pose' in cols:
                        cols.insert(1, cols.pop(cols.index('Pose')))
                        combined_data = combined_data[cols]

                    # Save the combined data to different segments based on time intervals
                    time_segments = [(8.47, 11.46, '_tx1'), 
                                    (16.47, 19.46, '_tx2'), 
                                    (24.47, 27.46, '_tx3')]
                                       
                    # Save the combined data to different segments based on time intervals
                    combined_filename = os.path.basename(vel_filepath).replace('_vel.tsv', '')
                    combined_filepath = os.path.join(base_dir, participant, 'PosVel_csv', combined_filename + '.csv')  # Change 'npy' to 'csv'

                    if not os.path.exists(os.path.dirname(combined_filepath)):
                        os.makedirs(os.path.dirname(combined_filepath))

                    for start_time, end_time, suffix in time_segments:
                        segment_data = combined_data[(combined_data['Time'] >= start_time) & (combined_data['Time'] <= end_time)]
                        
                        # Save the segment_data DataFrame as a CSV file
                        segment_filepath = combined_filepath.rsplit('.', 1)[0] + f'{suffix}.csv'  # Change '.npy' to '.csv'
                        segment_data.to_csv(segment_filepath, index=False)
                        print(f"Segmented data saved to {segment_filepath}")