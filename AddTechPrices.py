import pandas as pd
import re

# Define a hashmap with estimated prices
price_map = {
    'S20 FE': 300,
    'S21 FE': 400,
    'S20 PLUS': 450,
    'S20': 350,
    '13 MINI': 650,
    '14': 800,
    '13': 700,
    '12': 600,
    'XR': 400,
    '6S': 200,
    'A54': 250,
    'JETPACK MIFI 8800L': 100,
    'XCOVER PRO': 350
}

# Function to estimate price based on equipment model
def estimate_price(model):
    model_upper = model.upper()
    for key in price_map:
        # Adjust pattern to find key components of the model names
        pattern = re.compile(r'\b' + re.escape(key) + r'\b')
        if pattern.search(model_upper):
            return price_map[key]
    return 0  # Return 0 if no match is found

# Function to preprocess the model names to capture additional variations
def preprocess_model(model):
    # Remove common prefixes and extra spaces
    model = model.replace('GS', 'S').strip()
    return model

# Load the dataset
file_path = 'confidential/Merged_HH_Phone_Inventory_Plan.csv'
data = pd.read_csv(file_path)

# Preprocess the 'Equipment Model' column
data['Preprocessed Model'] = data['Equipment Model'].apply(preprocess_model)

# Add a new column for estimated prices
data['Estimated Price'] = data['Preprocessed Model'].apply(estimate_price)

# Drop the 'Preprocessed Model' column as it's no longer needed
data.drop(columns=['Preprocessed Model'], inplace=True)

# Save the updated data back to a new CSV file
output_file_path = 'confidential/AllPhoneInfo.csv' 
data.to_csv(output_file_path, index=False)

print(f"Data with estimated prices saved to {output_file_path}")
