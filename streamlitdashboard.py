import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder

# Authentication - Secure way to handle API keys or credentials without including it in the app's public files
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

anonymize = st.secrets["environment"].get("ANONYMIZE", "False") == "True"

# Anonymize user names if the environment variable is set to True
if anonymize:
    data_phone['Username'] = ['User ' + str(i) for i in range(len(data_phone))]

# Calculate summaries
total_inventory_value = data_server['Total Value'].sum()
total_annual_subscription = data_phone['Annual Charges'].sum()
phones_value = data_phone['Estimated Price'].sum()
storage_value = total_inventory_value  # Since all server items are in storage

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

# Pie Charts
st.subheader("Inventory and Subscription Distribution")

fig_inventory_pie = px.pie(data_server, values='Total Value', names='Section',
                           title="Storage Distribution by Category")
st.plotly_chart(fig_inventory_pie)

fig_subscription_pie = px.pie(data_phone, values='Annual Charges', names='Location',
                              title="Subscription Cost Distribution by Location")
st.plotly_chart(fig_subscription_pie)

data_phone['Administration'] = data_phone['Administration'].map({'Y': 'Yes', 'N': 'No'})
fig_admin_charges = px.bar(data_phone.groupby('Administration')['Annual Charges'].sum().reset_index(),
                           x='Administration', y='Annual Charges', title="Annual Phone Charges: Administration vs Non-Administration",
                           labels={'Annual Charges': 'Total Annual Charges ($)', 'Administration': 'Administration'},
                           color='Administration')
st.plotly_chart(fig_admin_charges)

# Interactive Data Tables with Download Buttons
st.subheader("Explore Data")

st.write("Phone Data")
grid_options = GridOptionsBuilder.from_dataframe(data_phone).build()
AgGrid(data_phone, gridOptions=grid_options)

phone_csv = data_phone.to_csv(index=False).encode('utf-8')
st.download_button(label="Download Phone Data as CSV", data=phone_csv, file_name='phone_data.csv', mime='text/csv')

st.write("Server Equipment Data")
grid_options = GridOptionsBuilder.from_dataframe(data_server).build()
AgGrid(data_server, gridOptions=grid_options)

server_csv = data_server.to_csv(index=False).encode('utf-8')
st.download_button(label="Download Server Data as CSV", data=server_csv, file_name='server_data.csv', mime='text/csv')

# Filtering Options
st.subheader("Filter Data")
selected_location = st.selectbox("Select Location", options=data_phone['Location'].unique())
filtered_data_phone = data_phone[data_phone['Location'] == selected_location]

st.write(f"Filtered Data for Location: {selected_location}")
grid_options = GridOptionsBuilder.from_dataframe(filtered_data_phone).build()
AgGrid(filtered_data_phone, gridOptions=grid_options)

filtered_phone_csv = filtered_data_phone.to_csv(index=False).encode('utf-8')
st.download_button(label=f"Download Filtered Phone Data for {selected_location} as CSV", data=filtered_phone_csv, file_name=f'filtered_phone_data_{selected_location}.csv', mime='text/csv')
