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

# Reducing gap between radio buttons and charts
st.markdown("""
    <style>
        .stRadio > div {
            margin-bottom: -20px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
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
            if is_high_level: st.rerun() # run script from beginning (will recognize authenication from session_state and avoid password prompt)

if st.session_state['authenticated']:
    # Loading screen
    with st.spinner('Loading dashboard...'):
        loading_message = st.empty()
        loading_message.success(f"Authentication with {st.session_state['clearance_level']} clearance successful.")

        st.title("Harvest Hope Tech Dashboard")

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
            try:
                # Use cached client
                client = get_gspread_client()
                sheet = client.open("HH Inventory").worksheet(worksheet_name)
                return pd.DataFrame(sheet.get_all_records())
            except Exception as e:
                st.error(f"Failed to load data from {worksheet_name}: {str(e)}")
                return pd.DataFrame()  # Return an empty DataFrame if there's an error

        # Processing Data
        @st.cache_data(show_spinner=False)
        def process_data(data):
            # Handles all sheets at once
            if 'RowID' in data.columns: # Only used by Shiny app
                data = data.drop(columns=['RowID'])
            if 'Total Charges' in data.columns:
                data['Total Charges'] = pd.to_numeric(data['Total Charges'].replace('[\$,]', '', regex=True), errors='coerce')
                data['Annual Phone Bill'] = data['Total Charges'] * 12
            if 'Estimated Price' in data.columns:
                data['Estimated Price'] = pd.to_numeric(data['Estimated Price'].replace('[\$,]', '', regex=True), errors='coerce')
                if 'Quantity' in data.columns:
                    data['Total Value'] = data['Quantity'] * data['Estimated Price']
            return data

        # Load and process data on first time
        if 'data_server' not in st.session_state:
            st.session_state.data_server = process_data(load_data('TechInventory'))

        if 'data_phone' not in st.session_state:
            st.session_state.data_phone = process_data(load_data('FullPhones'))

        if 'data_stationary' not in st.session_state:
            st.session_state.data_stationary = process_data(load_data('StationaryTech'))

        # Use session state data for rendering in the app
        data_server = st.session_state.data_server
        data_phone = st.session_state.data_phone.copy() # avoid modifying properties like usernames in the original. without .copy, they would refer to the same object.
        data_stationary = st.session_state.data_stationary

        # Anonymize names in data if user lacks sufficient clearance
        if st.session_state['clearance_level'] != 'high': # this will run every time - could be better optimized to store both censored and uncensored in session_state and choose which one.
            data_phone['Username'] = ['User ' + str(i) for i in range(len(data_phone))]
        
        # Summary Cards
        col1, col2, col3 = st.columns(3)
        col4, col5, col6, = st.columns(3)

        if not data_server.empty: 
            storage_value = data_server['Total Value'].sum()
            col3.metric("Total Storage Value", f"${storage_value:,.2f}", delta_color="off")
        if not data_phone.empty: 
            total_annual_phone_bill = data_phone['Annual Phone Bill'].sum()
            phones_value = data_phone['Estimated Price'].sum()
            col1.metric("Total Phone Value", f"${phones_value:,.2f}", delta_color="off")
            col5.metric("Total Annual Phone Bills", f"${total_annual_phone_bill:,.2f}", delta_color="off")
        if not data_stationary.empty: 
            stationary_value = data_stationary['Estimated Price'].sum()
            col2.metric("Total Workstation Device Value", f"${stationary_value:,.2f}", delta_color="off")

        if st.session_state['clearance_level'] == 'high': loading_message.empty() # If high level, they no longer need to see what authentication they signed in as -  they have everything.
    # (we loaded enough to end the spinner here)

    if not data_server.empty:
        chart_style = st.radio("Select Chart Style for Storage Value by Category:",
                            ('Bar Chart', 'Pie Chart'))

        if chart_style == 'Bar Chart':
            fig_server_value = px.bar(data_server.groupby('Combined_Section')['Total Value'].sum().reset_index(),
                                    x='Combined_Section', y='Total Value', title="Storage Value by Category",
                                    labels={'Combined_Section': 'Category'},
                                    color='Combined_Section')
            st.plotly_chart(fig_server_value)
        elif chart_style == 'Pie Chart':
            fig_inventory_pie = px.pie(data_server, values='Total Value', names='Combined_Section',
                                    title="Storage Value by Category")
            st.plotly_chart(fig_inventory_pie)

    if not data_phone.empty:
        fig_subscription_pie = px.pie(data_phone, values='Annual Phone Bill', names='Location',
                                    title="Subscription Cost by Location",
                                    color_discrete_sequence=px.colors.sequential.YlOrRd)
        
        data_phone['Administration'] = data_phone['Administration'].map({'Y': 'Yes', 'N': 'No'})
        fig_admin_charges = px.pie(data_phone.groupby('Administration')['Annual Phone Bill'].sum().reset_index(),
                                values='Annual Phone Bill', names='Administration',
                                title="Subscription Cost by Administration",
                                color_discrete_sequence=px.colors.sequential.Sunsetdark)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_subscription_pie)
        with col2:
            st.plotly_chart(fig_admin_charges)
    
    if not data_stationary.empty:
        chart_type = st.radio(
            "Select Chart Style for Total Value by Device Type:",
            ('Bar Chart', 'Pie Chart')
        )

        if chart_type == 'Bar Chart':
            fig_device = px.bar(
                data_stationary.groupby('Device')['Estimated Price'].sum().reset_index(),
                x='Device', 
                y='Estimated Price', 
                title="Total Value by Device Type",
                labels={'Estimated Price': 'Total Price', 'Device': 'Device Type'},
                color='Device'
            )
        elif chart_type == 'Pie Chart':
            fig_device = px.pie(
                data_stationary, 
                values='Estimated Price', 
                names='Device', 
                title="Total Value by Device Type",
                labels={'Estimated Price': 'Total Value'}
            )
        st.plotly_chart(fig_device)

    if not data_stationary.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_warehouse = px.pie(
                data_stationary.groupby('Warehouse')['Estimated Price'].sum().reset_index(),
                values='Estimated Price', 
                names='Warehouse', 
                title="Workstation Device Value by Warehouse",
                labels={'Estimated Price': 'Total Value'}
            )
            st.plotly_chart(fig_warehouse)

        with col2:
            fig_department = px.pie(
                data_stationary.groupby('Department')['Estimated Price'].sum().reset_index(),
                values='Estimated Price', 
                names='Department', 
                title="Workstation Device Value by Department",
                labels={'Estimated Price': 'Total Value'}
            )
            st.plotly_chart(fig_department)

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
        location_column = 'Location' if 'Location' in data.columns else 'Warehouse' # named different in different sheets
        # hypothetically, if multiple locations mapped to the same county, we would need to sum them which is what the next two lines do. currently for Harvest Hope, this is an impossible scenario, but it is handled.
        data['County'] = data[location_column].apply(get_county) # add new column
        data = data.groupby('County')[data_column].sum().reset_index() # override old data with nx2 data: each county name and summed data_column
        merged_data = pd.merge(all_counties_df, data[['County', data_column]], on='County', how='left') # Taking every row from all_counties and adding data_column from 'data' to it if 'data' has that county. 'data' technically only has 2 columns but we specify just to be safe.
        merged_data[data_column].fillna(default_value, inplace=True)
        return merged_data
    
    if not data_phone.empty:
        heatmap_data_counts = data_phone.groupby('Location').size().reset_index(name='Number of Phones')
        # heatmaps_data_counts example (indices aren't actually present)
        #        Location  Number of Phones
        #    0  Charleston            1
        #    1    Columbia            3
        #    2  Greenville            3
        
        # The locations are mapped to counties (Columbia -> Richland)
        # and counties not originally in the data_phone will have 'Number of Phones' set to the default value of 0.
        heatmap_data_counts = prepare_data(heatmap_data_counts, 'Number of Phones') # data is passed by reference

        heatmap_data_charges = data_phone.groupby('Location')['Annual Phone Bill'].sum().reset_index()
        heatmap_data_charges = prepare_data(heatmap_data_charges, 'Annual Phone Bill')

        heatmap_data_prices = data_phone.groupby('Location')['Estimated Price'].sum().reset_index()
        heatmap_data_prices = prepare_data(heatmap_data_prices, 'Estimated Price')

        # Radio buttons for heatmap selection
        heatmap_option = st.radio("Select Heatmap to Display", ('Number of Phones', 'Annual Phone Bill', 'Phone Valuation'))

        # Good color scales: YlOrRd, YlGnBu, Cividis, Portland
        scheme = "YlGnBu"
        if heatmap_option == 'Number of Phones':
            fig_heatmap = px.choropleth(heatmap_data_counts, geojson=geojson, locations='County', featureidkey="properties.name",
                                        color='Number of Phones', color_continuous_scale=scheme, title="Number of Phones by Warehouse")
        elif heatmap_option == 'Annual Phone Bill':
            fig_heatmap = px.choropleth(heatmap_data_charges, geojson=geojson, locations='County', featureidkey="properties.name",
                                        color='Annual Phone Bill', color_continuous_scale=scheme, title="Annual Phone Bill by Warehouse")
        else:
            fig_heatmap = px.choropleth(heatmap_data_prices, geojson=geojson, locations='County', featureidkey="properties.name",
                                        color='Estimated Price', color_continuous_scale=scheme, title="Phone Valuation by Warehouse")


        fig_heatmap.update_geos(fitbounds="locations", visible=True)
        fig_heatmap.update_traces(marker_line_width=0.5, marker_line_color='black')
        st.plotly_chart(fig_heatmap)

    if not data_stationary.empty:
        
        heatmap_data_prices = data_stationary.groupby('Warehouse')['Estimated Price'].sum().reset_index()
        heatmap_data_prices = prepare_data(heatmap_data_prices, 'Estimated Price')

        fig_heatmap = px.choropleth(heatmap_data_prices, geojson=geojson, locations='County', featureidkey="properties.name",
                                    color='Estimated Price', color_continuous_scale=scheme, title="Workstation Valuation by Warehouse")

        fig_heatmap.update_geos(fitbounds="locations", visible=True)
        fig_heatmap.update_traces(marker_line_width=0.5, marker_line_color='black')
        st.plotly_chart(fig_heatmap)

    # Interactive Data Tables with Download Buttons
    st.subheader("Explore Data")

    # Phone Data
    if not data_phone.empty:
        location_options = ['All'] + list(data_phone['Location'].unique())
        selected_location = st.selectbox("Select Location:", options=location_options)

        # Filter data based on selected location
        if selected_location != 'All':
            filtered_data_phone = data_phone[data_phone['Location'] == selected_location]
        else:
            filtered_data_phone = data_phone

        # Display the data table
        st.write(f"Phone Data for {selected_location}:")
        grid_options = GridOptionsBuilder.from_dataframe(filtered_data_phone).build()
        AgGrid(filtered_data_phone, gridOptions=grid_options)

        # Download button for the displayed data
        phone_csv = filtered_data_phone.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Displayed Phone Data as CSV",
                        data=phone_csv,
                        file_name=f'phone_data_{selected_location.replace(" ", "_")}.csv',
                        mime='text/csv')

    # Server Data
    if not data_server.empty:
        section_options = ['All'] + list(data_server['Section'].unique())
        selected_section = st.selectbox("Select Section:", options=section_options)

        # Filter data based on selected section
        if selected_section != 'All':
            filtered_data_server = data_server[data_server['Section'] == selected_section]
        else:
            filtered_data_server = data_server

        # Prepare data for display (dropping 'Combined_Section' if it exists)
        data_server_display = filtered_data_server.copy()  # Work with the filtered data
        if 'Combined_Section' in data_server_display.columns:
            data_server_display = data_server_display.drop(columns=['Combined_Section'])

        # Display the data table
        st.write(f"Server Equipment Data for: {selected_section}")
        grid_options = GridOptionsBuilder.from_dataframe(data_server_display).build()
        AgGrid(data_server_display, gridOptions=grid_options)

        # Download button for the displayed data
        server_csv = filtered_data_server.to_csv(index=False).encode('utf-8') # We might as well let them download with Combined_Section but it wasn't worth displaying
        st.download_button(label="Download Displayed Server Data as CSV", 
                        data=server_csv,
                        file_name=f'server_data_{selected_section.replace(" ", "_")}.csv',
                        mime='text/csv')
        
    # Workstation Data - complex two-tier filtering system because there are multiple columns of interest you might want to filter by, and each obviously have categories
    if not data_stationary.empty:
        filter_categories = ['Department', 'Device', 'Warehouse']

        selected_filter_category = st.selectbox("Select a filter category:", ['All'] + filter_categories)

        if selected_filter_category != 'All':
            unique_values = sorted(data_stationary[selected_filter_category].unique()) # alphabetically displayed
            selected_value = st.selectbox(f"Select {selected_filter_category}:", ['All'] + unique_values) # only prompt for tier 2 if they have selected a filter in tier 1
        else:
            selected_value = 'All'

        if selected_value != 'All':
            filtered_data = data_stationary[data_stationary[selected_filter_category] == selected_value]
        else:
            filtered_data = data_stationary

        if selected_filter_category != 'All' and selected_value != 'All':
            display_text = f"{selected_filter_category} - {selected_value}"
        else:
            display_text = "All"
            
        st.write(f"Workstation Device Data for {display_text}:")

        st.dataframe(filtered_data)

        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Displayed Workstation Data as CSV",
            data=csv,
            file_name=f"{selected_filter_category.lower()}_{selected_value.replace(' ', '_').lower()}_data.csv",
            mime='text/csv'
        )

elif password != "":
        st.error("The password you entered is incorrect. Please try again.")