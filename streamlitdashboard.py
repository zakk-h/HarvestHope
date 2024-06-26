import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import hashlib
import json

# Password Hash
low_level_hash = st.secrets["clearance"]["low_level"]
high_level_hash = st.secrets["clearance"]["high_level"]

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'clearance_level' not in st.session_state:
    st.session_state['clearance_level'] = None

# Ask for password
if st.session_state['clearance_level'] != 'high':
    password = st.text_input("Enter the password to access the dashboard:", type="password")

    if password: # if password is 'truthy' - not None, empty string, etc

        # Function to verify the password
        def verify_password(user_input, hashed):
            return hashlib.sha256(user_input.encode()).hexdigest() == hashed
        
        is_high_level = verify_password(password, high_level_hash)  
        is_low_level = verify_password(password, low_level_hash)
        if is_high_level or is_low_level: # sufficient clearance
            st.session_state['authenticated'] = True
            st.session_state['clearance_level'] = 'high' if is_high_level else 'low'
            st.success(f"Authenticated with {st.session_state['clearance_level']} level clearance")
            if is_high_level: st.rerun() # run script from beginning (will recognize authenication from session_state and avoid password prompt)

if st.session_state['authenticated']:

    # Loading screen placeholder
    loading_message = st.empty()
    loading_message.text("Loading the dashboard... Please wait.")

    # Cache the scope, credentials, and client authorization
    @st.cache_resource
    def get_gspread_client():
        # Authentication - Secure way to handle API keys or credentials without including it in the app's public files
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client
 
    # Load data from Google Sheets
    @st.cache_data(show_spinner=False)
    def load_data(worksheet_name):
        # Use cached client
        client = get_gspread_client()
        sheet = client.open("HH Inventory").worksheet(worksheet_name)
        return pd.DataFrame(sheet.get_all_records())

    # Processing Data
    @st.cache_data(show_spinner=False)
    def process_data(data):
        if 'RowID' in data.columns: # Only used by Shiny app
            data = data.drop(columns=['RowID'])
        if 'Total Charges' in data.columns:
            data['Total Charges'] = pd.to_numeric(data['Total Charges'].replace('[\$,]', '', regex=True), errors='coerce')
            data['Annual Charges'] = data['Total Charges'] * 12
        if 'Estimated Price' in data.columns:
            data['Estimated Price'] = pd.to_numeric(data['Estimated Price'].replace('[\$,]', '', regex=True), errors='coerce')
            if 'Quantity' in data.columns:
                data['Total Value'] = data['Quantity'] * data['Estimated Price']
        return data

    # Load and process data on first time
    if 'data_server' not in st.session_state:
        st.session_state.data_server = process_data(load_data('testcompat'))

    if 'data_phone' not in st.session_state:
        st.session_state.data_phone = process_data(load_data('PhoneSandbox'))

    # Use session state data for rendering in the app
    data_server = st.session_state.data_server
    data_phone = st.session_state.data_phone.copy() # avoid modifying properties like usernames in the original. without .copy, they would refer to the same object.

    # Anonymize names in data if user lacks sufficient clearance
    if st.session_state['clearance_level'] != 'high':
        data_phone['Username'] = ['User ' + str(i) for i in range(len(data_phone))]

    # Calculate summaries
    storage_value = data_server['Total Value'].sum()
    total_annual_subscription = data_phone['Annual Charges'].sum()
    phones_value = data_phone['Estimated Price'].sum()

    st.title("Harvest Hope Tech Dashboard")

    # Summary Cards
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Annual Subscriptions", f"${total_annual_subscription:,.2f}")
    col2.metric("Total Phones Value", f"${phones_value:,.2f}")
    col3.metric("Total Storage Value", f"${storage_value:,.2f}")

    loading_message.empty() # We loaded enough to justify removing the loading screen message

    # Bar Chart: Inventory Value by Category
    fig_server_value = px.bar(data_server.groupby('Combined_Section')['Total Value'].sum().reset_index(),
                            x='Combined_Section', y='Total Value', title="Storage Value by Category",
                            labels={'Total Value': 'Total Value ($)', 'Section': 'Category'},
                            color='Combined_Section')
    st.plotly_chart(fig_server_value)

    # Bar Chart: Annual Phone Charges by Location
    fig_phone_charges = px.bar(data_phone.groupby('Location')['Annual Charges'].sum().reset_index(),
                            x='Location', y='Annual Charges', title="Annual Phone Charges by Location",
                            labels={'Annual Charges': 'Total Annual Charges ($)', 'Location': 'Location'},
                            color='Location')
    st.plotly_chart(fig_phone_charges)

    # Pie Charts
    st.subheader("Inventory and Subscription Distribution")

    fig_inventory_pie = px.pie(data_server, values='Total Value', names='Combined_Section',
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

    # Load GeoJSON data for South Carolina counties
    @st.cache_data(show_spinner=False)
    def load_geojson():
        with open('south_carolina_counties.geojson') as f:
            return json.load(f)

    geojson = load_geojson()

    all_counties = ["Abbeville", "Aiken", "Allendale", "Anderson", "Bamberg", "Barnwell", "Beaufort", "Berkeley", "Calhoun", "Charleston", "Cherokee", "Chester", "Chesterfield", "Clarendon", "Colleton", "Darlington", "Dillon", "Dorchester", "Edgefield", "Fairfield", "Florence", "Georgetown", "Greenville", "Greenwood", "Hampton", "Horry", "Jasper", "Kershaw", "Lancaster", "Laurens", "Lee", "Lexington", "McCormick", "Marion", "Marlboro", "Newberry", "Oconee", "Orangeburg", "Pickens", "Richland", "Saluda", "Spartanburg", "Sumter", "Union", "Williamsburg", "York"]
    #all_counties = [feature['properties']['name'] for feature in geojson['features']]
    
    # Convert this list into a DataFrame
    all_counties_df = pd.DataFrame(all_counties, columns=['County'])


    # Function to map location to county for Harvest Hope offices
    def get_county(location):
        if location == "Columbia":
            return "Richland"
        return location

    # Merge the existing data with this complete list
    # First convert cities to counties (it is an injective map) and then add all other counties with default value 0
    @st.cache_data(show_spinner=False)
    def prepare_data(data, data_column, default_value=0):
        # hypothetically, if multiple locations mapped to the same county, we would need to sum them which is what the next two lines do. currently for Harvest Hope, this is an impossible scenario, but it is handled.
        data['County'] = data['Location'].apply(get_county) # add new column
        data = data.groupby('County')[data_column].sum().reset_index() # override old data with nx2 data: each county name and summed data_column
        merged_data = pd.merge(all_counties_df, data[['County', data_column]], on='County', how='left') # Taking every row from all_counties and adding data_column from 'data' to it if 'data' has that county. 'data' technically only has 2 columns but we specify just to be safe.
        merged_data[data_column].fillna(default_value, inplace=True)
        return merged_data
    
    heatmap_data_counts = data_phone.groupby('Location').size().reset_index(name='Phone Counts')
    # heatmaps_data_counts example (indices aren't actually present)
    #        Location  Phone Counts
    #    0  Charleston            1
    #    1    Columbia            3
    #    2  Greenville            3
    
    # The locations are mapped to counties (Columbia -> Richland)
    # and counties not originally in the data_phone will have 'Phone Counts' set to the default value of 0.
    heatmap_data_counts = prepare_data(heatmap_data_counts, 'Phone Counts') # data is passed by reference

    heatmap_data_charges = data_phone.groupby('Location')['Annual Charges'].sum().reset_index()
    heatmap_data_charges = prepare_data(heatmap_data_charges, 'Annual Charges')

    heatmap_data_prices = data_phone.groupby('Location')['Estimated Price'].sum().reset_index()
    heatmap_data_prices = prepare_data(heatmap_data_prices, 'Estimated Price')

    # Radio buttons for heatmap selection
    heatmap_option = st.radio("Select Heatmap to Display", ('Phone Counts', 'Annual Phone Charges', 'Estimated Price of Phones'))

    # Good color scales: YlOrRd, YlGnBu, Cividis, Portland
    scheme = "YlGnBu"
    if heatmap_option == 'Phone Counts':
        fig_heatmap = px.choropleth(heatmap_data_counts, geojson=geojson, locations='County', featureidkey="properties.name",
                                    color='Phone Counts', color_continuous_scale=scheme, title="Phone Counts by County in South Carolina")
    elif heatmap_option == 'Annual Phone Charges':
        fig_heatmap = px.choropleth(heatmap_data_charges, geojson=geojson, locations='County', featureidkey="properties.name",
                                    color='Annual Charges', color_continuous_scale=scheme, title="Annual Phone Charges by County in South Carolina")
    else:
        fig_heatmap = px.choropleth(heatmap_data_prices, geojson=geojson, locations='County', featureidkey="properties.name",
                                    color='Estimated Price', color_continuous_scale=scheme, title="Estimated Price of Phones by County in South Carolina")


    fig_heatmap.update_geos(fitbounds="locations", visible=True)
    fig_heatmap.update_traces(marker_line_width=0.5, marker_line_color='black')
    st.plotly_chart(fig_heatmap)

    # Interactive Data Tables with Download Buttons
    st.subheader("Explore Data")

    st.write("Phone Data")
    grid_options = GridOptionsBuilder.from_dataframe(data_phone).build()
    AgGrid(data_phone, gridOptions=grid_options)

    phone_csv = data_phone.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Phone Data as CSV", data=phone_csv, file_name='phone_data.csv', mime='text/csv')

    st.write("Server Equipment Data")
    # Combined Section isn't worth displaying in the data table - drop it after it has been used in visualization
    data_server_display = data_server.copy() # New object
    if 'Combined_Section' in data_server_display.columns:
        data_server_display = data_server_display.drop(columns=['Combined_Section'])    
    grid_options = GridOptionsBuilder.from_dataframe(data_server_display).build()
    AgGrid(data_server_display, gridOptions=grid_options)

    server_csv = data_server.to_csv(index=False).encode('utf-8') # They can download with combined section here because they might as well have everything - it just hurts the user interface to include it in the app table
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
elif password != "":
        st.error("The password you entered is incorrect. Please try again.")