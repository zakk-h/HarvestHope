# Harvest Hope Inventory Management Dashboards and Scripts





## Introduction
This repository hosts scripts to edit and merge spreadsheets or CSV files, as well as two web applications that serve as workbooks or dashboards for Harvest Hope's inventory and assets. The Streamlit and Shiny applications are briefly described and linked below, and then full documentation for each is provided later in the readme. 

### Streamlit App
This Streamlit application was developed to provide a centralized dashboard for managing and visualizing all tech equipment and contracts for Harvest Hope. The application connects directly to Google Sheets to fetch the latest data for all equipment and contracts for each employee, tracking company assets.

You can access the live app [here](https://hhequipment.streamlit.app).

### Shiny App
This Shiny application was developed to manage and visualize inventory data for Harvest Hope. The primary purpose of the application is to provide an interactive and user-friendly interface for viewing, editing, and updating inventory records, which were previously maintained in a spreadsheet. 
You can access the live app <a href="https://zakk-h.shinyapps.io/harvesthope" target="_blank">here</a>.

# Asset Management Streamlit App Documentation

## Overview
This Streamlit application was developed to provide a centralized dashboard for managing and visualizing all tech equipment and contracts for Harvest Hope, a non-profit organization. The application connects directly to Google Sheets to fetch the latest data, offering an interactive and user-friendly interface for viewing, editing, and updating records. This centralized workbook accounts for all equipment and contracts for each employee, tracking company assets and providing valuable insights.

You can access the live app [here](https://hhequipment.streamlit.app).

<a href="https://hhequipment.streamlit.app" target="_blank">
  <img src="https://img.shields.io/badge/Streamlit-app-blue" alt="Streamlit App">
</a>

## Features
- **Data Visualization**: Provides various visualizations including bar charts, pie charts, and heatmaps to represent inventory and subscription data.
- **Interactive Data Tables**: Displays inventory data in a searchable and sortable table.
- **Summary Cards**: Shows key metrics like total inventory value, total annual subscription costs, and total phones value.
- **Data Integration with Google Sheets**: Connects directly to Google Sheets through a service account to fetch and display real-time data. The credentials required for accessing Google Sheets with the same privileges as the service account are securely stored in the .streamlit/secrets.toml file, ensuring that sensitive information is not exposed to users when the app is hosted. This integration allows seamless synchronization of data without manual uploads or updates.
- **Data Anonymization**: Option to anonymize user data (names, etc) that were entered into sheets when displayed in the app for privacy. When the anonymization flag is enabled, all personal identifiers are replaced with generic labels (e.g., "User 1", "User 2"). This ensures that sensitive information is not visible to app users. The anonymization setting is managed through a flag stored in the .streamlit/secrets.toml file, which is part of the backend. This setup ensures that the flag is inaccessible to users and consistently enforces privacy policies.
- **Download Data**: Option to download the current displayed data tables as a CSV file.

## Getting Started

### Installation
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Configuration
Create a `.streamlit/secrets.toml` file to store your Google Sheets API credentials and anonymization setting:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = '''
-----BEGIN PRIVATE KEY-----
your_private_key
-----END PRIVATE KEY-----
'''
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your_client_email"
universe_domain = "googleapis.com"

[app_settings]
anonymize = true
```

### Running the App
Run the application using the following command:
```bash
streamlit run streamlitdashboard.py
```

# Inventory Management Shiny App Documentation

## Overview
This Shiny application was developed to manage and visualize inventory data for Harvest Hope, a non-profit organization. The primary purpose of the application is to provide an interactive and user-friendly interface for viewing, editing, and updating inventory records, which were previously maintained in a spreadsheet. 
You can access the live app <a href="https://zakk-h.shinyapps.io/harvesthope" target="_blank">here</a>.

<a href="https://zakk-h.shinyapps.io/harvesthope" target="_blank">
  <img src="https://img.shields.io/badge/Shiny-app-blue" alt="Shiny App">
</a>

## Features
- **Data Visualization**: Provides a bar plot visualization of the total quantity of items by section.
- **Interactive Data Table**: Displays inventory data in a searchable and sortable table with the ability to update item quantities directly from the interface.
- **Add Items**: Allows authorized users to add new items to the inventory.
- **Admin Authentication**: Secured login system to restrict certain functionalities to admin users.
- **Download Data**: Option to download the current inventory data as a CSV file.
- **Item Merging**: Automatically collapses items with the same name and comments, even if they are tagged in different sections, simplifying data entry.

## Getting Started

## Installation
Install the required packages:
```R
install.packages(c("shiny", "tidyverse", "plotly", "DT", "shinyjs", "sodium", "googlesheets4"))
```

## Running the App
Open the app.R file in RStudio.
Run the application by clicking the "Run App" button in RStudio or by using the command:
```R
shiny::runApp()
```
## Using the App
- **Sections Filter**: Select sections to filter the inventory data displayed.
- **Add Item Form**: Fields to enter the item name, quantity, comments, and section.
- **Admin Panel**: Password input and login button for admin authentication.
- **Data Table**: Interactive table with plus and minus buttons to adjust item quantities.
- **Bar Plot**: Visualization of the total quantity of items by combined sections.
- **Admin Authentication**: Only authenticated users can add items to the inventory or modify item quantities. Admin login requires a password, which is securely hashed and compared using the sodium package.
- **Data Handling**: The inventory data is initially loaded from a CSV file named TechInventory.csv.Changes made to the inventory data are written back to the CSV file to ensure persistence. Users can download the current state of the inventory data as a CSV file.

## Issues and Considerations
- **State Resetting**: When updating the data table, the state (e.g., current page, search filters) resets. This can be inconvenient for users making multiple edits. Considerations for improvement include maintaining state between updates.
- **Concurrency**: Concurrent modifications by multiple users can lead to data inconsistencies. For example, if two users update the inventory simultaneously, the last write wins, potentially overwriting the first user's changes. 

## Future Enhancements
- Transitioning from CSV to Google Sheets or a database system for real-time updates, concurrent modification, and improved data consistency.
- Adding features such as time-based notifications, change history, and the ability to update item sections.

# Scripts
Additionally, there are several scripts included in the project that can perform the following tasks:
- Estimate the price of phone models based on predefined criteria.
- Use a language model to generate price estimates for phone models. The GPT-2 model runs locally and provides a free method for estimating prices without the same casework and predefined criteria, but as it is a text-generation model without real-time data, it is very inaccurate.
- Merge data from different CSV files to create a comprehensive dataset of billing and subscription information.
