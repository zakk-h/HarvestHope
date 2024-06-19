import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import numpy as np
import os

# Authenication - Secure way to handle API keys or credentials without including it in the app's public files
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Load data from Google Sheets
def load_data(worksheet_name):
    sheet = client.open("HH Inventory").worksheet(worksheet_name)
    return pd.DataFrame(sheet.get_all_records())

# Processing Data
def process_data(data):
    if 'Total Charges' in data.columns:
        data['Total Charges'] = pd.to_numeric(data['Total Charges'].replace('[\$,]', '', regex=True), errors='coerce')
        data['Annual Charges'] = data['Total Charges'] * 12
    if 'Estimated Price' in data.columns:
        data['Estimated Price'] = pd.to_numeric(data['Estimated Price'].replace('[\$,]', '', regex=True), errors='coerce')
    if 'Quantity' in data.columns:
        data['Total Value'] = data['Quantity'] * data['Estimated Price']
    return data

# Load and process data
data_server = process_data(load_data('ServerSandbox'))
data_phone = process_data(load_data('PhoneSandbox'))

anonymize = os.getenv('ANONYMIZE', 'False') == 'True'

# Anonymize user names if the environment variable is set to True
if anonymize:
    data_phone['Username'] = ['User ' + str(i) for i in range(len(data_phone))]

# Calculate summaries
total_inventory_value = data_server['Total Value'].sum()
total_annual_subscription = data_phone['Annual Charges'].sum()
phones_value = data_phone['Estimated Price'].sum()
storage_value = total_inventory_value  # Since all server items are in storage

# Dashboard Title
st.title("Harvest Hope Tech Dashboard")

# Summary Cards
st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Annual Subscription", f"${total_annual_subscription:,.2f}")
col2.metric("Total Phones Value", f"${phones_value:,.2f}")
col3.metric("Total Storage Value", f"${storage_value:,.2f}")

# Bar Chart: Inventory Value by Category
fig_server_value = px.bar(data_server.groupby('Section')['Total Value'].sum().reset_index(),
                          x='Section', y='Total Value', title="Storage Value by Category",
                          labels={'Total Value': 'Total Value ($)', 'Section': 'Category'},
                          color='Section')
st.plotly_chart(fig_server_value)

# Bar Chart: Annual Phone Charges by Location
fig_phone_charges = px.bar(data_phone.groupby('Location')['Annual Charges'].sum().reset_index(),
                           x='Location', y='Annual Charges', title="Annual Phone Charges by Location",
                           labels={'Annual Charges': 'Total Annual Charges ($)', 'Location': 'Location'},
                           color='Location')
st.plotly_chart(fig_phone_charges)

# Heatmap: Distribution of Phone Costs Across Locations
#heatmap_data = data_phone.groupby('Location')['Estimated Price'].sum().reset_index()
#heatmap_data['Log Price'] = np.log1p(heatmap_data['Estimated Price'])  # Use log scale for better visualization

#fig_heatmap = px.density_heatmap(heatmap_data, x='Location', y='Log Price', z='Estimated Price',
#                                 title="Heatmap of Phone Costs by Location",
#                                 labels={'Log Price': 'Log of Estimated Price ($)', 'Location': 'Location'},
#                                 color_continuous_scale='Viridis')
#st.plotly_chart(fig_heatmap)

# Pie Charts
st.subheader("Inventory and Subscription Distribution")

fig_inventory_pie = px.pie(data_server, values='Total Value', names='Section',
                           title="Storage Distribution by Category")


st.plotly_chart(fig_inventory_pie)

col4, col5 = st.columns(2)


fig_subscription_pie = px.pie(data_phone, values='Annual Charges', names='Location',
                              title="Subscription Cost Distribution by Location")
col4.plotly_chart(fig_subscription_pie)

data_phone['Administration'] = data_phone['Administration'].map({'Y': 'Yes', 'N': 'No'})
fig_admin_charges = px.bar(data_phone.groupby('Administration')['Annual Charges'].sum().reset_index(),
                           x='Administration', y='Annual Charges', title="Annual Phone Charges: Administration vs Non-Administration",
                           labels={'Annual Charges': 'Total Annual Charges ($)', 'Administration': 'Administration'},
                           color='Administration')
col5.plotly_chart(fig_admin_charges)

# Interactive Data Tables
st.subheader("Explore Data")
st.write("Phone Data")
st.dataframe(data_phone)

st.write("Server Equipment Data")
st.dataframe(data_server)

# Filtering Options
st.subheader("Filter Data")
selected_location = st.selectbox("Select Location", options=data_phone['Location'].unique())
filtered_data_phone = data_phone[data_phone['Location'] == selected_location]

st.write(f"Filtered Data for Location: {selected_location}")
st.dataframe(filtered_data_phone)
