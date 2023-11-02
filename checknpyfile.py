import pandas as pd

# Specify the path to your .csv file
csv_filepath = '/media/dcope/DC_LaCie/Yoga_Study_MOCAP_Data/01/PosVel_csv/01_CRW2L_MC_V1_tx1.csv'

# Load the .csv file into a pandas DataFrame
df = pd.read_csv(csv_filepath)

# Display the DataFrame
print(df)

# If you want to save the DataFrame to another CSV or different format:
# df.to_csv('output_filename.csv', index=False)
