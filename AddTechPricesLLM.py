import pandas as pd
import re
from transformers import pipeline
# Very unreliable way to get prices of inventory (Running GPT-2 model locally). 
# GPT-2, an LLM that focuses on text and not so much numerics struggles here and does not have access to real time data. But, it is free.
# Do not use for anything remotely important - for experimentation only.

# Initialize the model
generator = pipeline('text-generation', model='gpt2')

# Function to get the estimated price from GPT-2
def get_price_from_llm(model_name):
    prompt = f"The price of a {model_name} in USD is what? Please only return the price in US dollars. I would expect these phones to be anywhere from 100 to 1400 USD. iPhones are probably roughly 500-800. Samsung S20s-S22s are probably similar too. Do not return a value less than 100."
    #prompt = "Say exactly the following back to me and nothing else: 117"
    response = generator(prompt, max_new_tokens=30, num_return_sequences=1, truncation=True)
    try:
        # Extract the price from the response
        price_text = response[0]['generated_text']
        price = float(re.findall(r'\d+', price_text)[0]) # Take the first numerical value found.
    except Exception as e:
        print(f"Error parsing response for model {model_name}: {e}")
        price = 0  # Default to 0 if extraction fails
    return price

# Load the dataset
file_path = 'confidential/Merged_HH_Phone_Inventory_Plan.csv'  
data = pd.read_csv(file_path)

# Get unique models to reduce LLM calls
unique_models = data['Equipment Model'].unique()

# Create a price map by calling the LLM for each unique model
price_map = {}
for model in unique_models:
    price_map[model] = get_price_from_llm(model)

# Function to estimate price based on equipment model using the price map
def estimate_price(model):
    return price_map.get(model, 0)

# Add a new column for estimated prices
data['Estimated Price'] = data['Equipment Model'].apply(estimate_price)

# Save the updated data back to a new CSV file
output_file_path = 'confidential/AllPhoneInfo.csv'
data.to_csv(output_file_path, index=False)

print(f"Data with estimated prices saved to {output_file_path}")
