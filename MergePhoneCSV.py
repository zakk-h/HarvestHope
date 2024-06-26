import pandas as pd

# Load the data from the CSV files
hh_inventory_path = 'confidential/PhoneInventory.csv'
vzw_mobile_plans_path = 'confidential/PhonePlans.csv'

# Ensure that the Device ID column is read as a string to avoid scientific notation
hh_inventory_df = pd.read_csv(hh_inventory_path, dtype={'Device ID': str})
vzw_mobile_plans_df = pd.read_csv(vzw_mobile_plans_path, dtype={'Device ID': str})

# Cleaning and preparing the HH Inventory dataframe
hh_inventory_df.columns = hh_inventory_df.iloc[0]
hh_inventory_df = hh_inventory_df[1:].reset_index(drop=True)

# Cleaning and preparing the VZW Mobile Plans dataframe
vzw_mobile_plans_df.columns = vzw_mobile_plans_df.iloc[4]
vzw_mobile_plans_df = vzw_mobile_plans_df[5:].reset_index(drop=True)

# Splitting the "Number / User Name" column to extract the phone number
vzw_mobile_plans_df[['Number', 'User Name']] = vzw_mobile_plans_df['Number / User Name'].str.extract(r'(\d{3}-\d{3}-\d{4})\s*(.*)')
vzw_mobile_plans_df['Number'] = vzw_mobile_plans_df['Number'].str.replace('-', '.')

# Adding Administration Y/N based on the presence of "ADMIN" in the "Cost Center" column
vzw_mobile_plans_df['Administration'] = vzw_mobile_plans_df.apply(
    lambda row: 'Y' if 'ADMIN' in str(row['Cost Center']).upper() else 'N', axis=1
)

# Renaming the column in HH Inventory to match VZW for merging
hh_inventory_df = hh_inventory_df.rename(columns={'Mobile Number': 'Number'})

# Merging the dataframes on the phone number
merged_df = pd.merge(hh_inventory_df, vzw_mobile_plans_df, on='Number', how='left')

# Selecting relevant columns for the final merged dataframe
final_columns = [
    'Number', 'Username', 'Equipment Model', 'Device ID', 'Location', 'Administration', 'Storage',
    'Monthly Access Charges', 'Usage Charges', 'Equipment Charges', 
    'Surcharges and Other Charges and Credits', 'Taxes Governmental Surcharges and Fees', 
    'Third Party Charges (Includes Tax)', 'Total Charges'
]
merged_df = merged_df[final_columns]

# Save the merged dataframe to a new CSV file without scientific notation
merged_file_path = 'confidential/Merged_HH_Phone_Inventory_Plan.csv'
merged_df.to_csv(merged_file_path, index=False, float_format='%.0f')

print(f'Merged file saved to: {merged_file_path}')
