import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px

# streamlit run streamlitdashboard.py

# Authentication and Setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('confidential/hhinventory_service_account_credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("HH Inventory").worksheet('Sandbox')

# Fetch data
data = pd.DataFrame(sheet.get_all_records())

# Convert financial data to numeric
data['Total Charges'] = pd.to_numeric(data['Total Charges'].str.replace('$', ''), errors='coerce')
data['Estimated Price'] = pd.to_numeric(data['Estimated Price'], errors='coerce')

# Calculate annual total charges and total estimated price
data['Annual Total Charges'] = data['Total Charges'] * 12
annual_charges = data['Annual Total Charges'].sum()
total_price = data['Estimated Price'].sum()

# Display calculations
st.header("Harvest Hope Phone Summary")
st.subheader(f"Annual Cell Phone Bill: ${annual_charges:,.2f}")
st.subheader(f"Total Price of All Phones: ${total_price:,.2f}")

# Create and display plots
st.header("Data Breakdown")
fig_loc = px.bar(data.groupby('Location')['Annual Total Charges'].sum().reset_index(), x='Location', y='Annual Total Charges', title="Total Charges by Location")
st.plotly_chart(fig_loc)

fig_admin = px.bar(data[data['Administration'] == 'Y'].groupby('Location')['Annual Total Charges'].sum().reset_index(), x='Location', y='Annual Total Charges', title="Total Charges by Administration")
st.plotly_chart(fig_admin)

# Interactive data sheet with editing capability
st.header("Editable Data Sheet")
st.dataframe(data)

