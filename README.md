# Harvest Hope Inventory Management Dashboards and Scripts





## Introduction
This repository hosts scripts to edit and merge spreadsheets or CSV files, as well as two web applications that serve as workbooks or dashboards for Harvest Hope's inventory and assets. The Streamlit and Shiny applications are briefly described and linked below, and then full documentation for each is provided later in the readme. 

### Streamlit App
This Streamlit application was developed to provide a centralized dashboard for managing and visualizing all tech equipment and contracts for Harvest Hope. The application connects directly to Google Sheets to fetch the latest data for all equipment and contracts for each employee, tracking company assets.

You can access the live app [here](https://hhequipment.streamlit.app).

### Shiny App
This Shiny application was developed to manage and visualize inventory data for Harvest Hope. The primary purpose of the application is to provide an interactive and user-friendly interface for viewing, editing, and updating inventory records, all directly connected to a Google Sheet. 

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
- **Passwords and Authentication**: The Streamlit app features a two-tiered authentication system that ensures different levels of data access and security. Users can gain either 'low-level' or 'high-level' clearance based on the password they provide. When a user enters a password, the app uses SHA-256 hashing to convert the entered password into a hash. 
This hash is then compared against pre-stored hashes in the `.streamlit/secrets.toml` file, which is not accessible to end users (it is a part of the backend). If the hash matches the 'high-level' password hash, the user is granted high-level clearance; if it matches the 'low-level' hash, the user receives low-level clearance. If neither is met, the user cannot access any part of the app.
- **Data Anonymization**: When the user only has 'low-level' authentication, the app anonymizes user data (names, etc) that was entered into sheet when displayed in the app for privacy. When this anonymization flag is enabled, all personal identifiers are replaced with generic labels (e.g., "User 1", "User 2"). This ensures that sensitive information is not visible to lower level users. 

- **Download Data**: Option to download the current displayed data tables as a CSV file.

## Getting Started

### Installation
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Configuration
First, ensure you have a Google Cloud Platform (GCP) project and have created a service account with permissions to access Google Sheets. For instructions, see the [Service Account Setup Guide](service_account_help.md).

The app uses SHA-256 hashes for password verification to manage user access levels. 

Create a `.streamlit/secrets.toml` file to store your Google Sheets API credentials and valid, pre-defined SHA-256 password hashes and replace the placeholders below:
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

[clearance]
low_level = "your_low_level_sha256_hash"
high_level = "your_high_level_sha256_hash"
```

#### Generating Password Hashes in Python

You can generate SHA-256 password hashes using Python. Here's a simple script to hash your passwords:

```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

password1 = "your_first_password"
password2 = "your_second_password"

hashed_password1 = hash_password(password1)
hashed_password2 = hash_password(password2)

print(f"Hashed Password 1: {hashed_password1}")
print(f"Hashed Password 2: {hashed_password2}")
```


### Running the App
Run the application using the following command:
```bash
streamlit run streamlitdashboard.py
```

# Inventory Management Shiny App Documentation

## Overview
This Shiny application was developed to manage and visualize inventory data for Harvest Hope, a non-profit organization. The primary purpose of the application is to provide an interactive and user-friendly interface for viewing, editing, and updating inventory records through a behind-the-scenes spreadsheet. Whether in the office or out in the field surveying inventory, users can easily modify item quantities with intuitive plus and minus buttons or add new items on the go. They don't need to worry about adding a new line item for a model that already exists - the app will catch it and collapse them.

You can access the live app <a href="https://zakk-h.shinyapps.io/harvesthope" target="_blank">here</a>.

<a href="https://zakk-h.shinyapps.io/harvesthope" target="_blank">
  <img src="https://img.shields.io/badge/Shiny-app-blue" alt="Shiny App">
</a>

## Features
- **Data Visualization**: The inventory dashboard features two primary bar plots to help visualize your inventory data effectively: Total Quantity or Total Price per Section. A sleek and intuitive navigation bar featuring Font Awesome circles allows you to switch between the two bar plots seamlessly, highlighting the circle that corresponds to the active page.  
- **Interactive Data Table**: Displays inventory data in a searchable and sortable table with the ability to update item quantities directly from the interface.
- **Data Entry**: Allows authorized users to add new items to the inventory in the side panel with drop down categories or edit quantities of existing items with the plus or minus buttons embedded in the data table.
- **Google Sheets Connection**: The app integrates directly with Google Sheets, ensuring real-time data synchronization. This allows users to maintain accurate inventory records without manual data entry or updates. The Google Sheets API credentials are securely stored in a JSON file (`confidential/hhinventory_service_account_credentials.json`).
- **Fresh Data**: The app always pulls the latest spreadsheet data before making any changes such as increasing or decreasing item quantities or adding new items. This ensures that pushed changes would never "roll back" other changes if another user modified another row. In the case of increments or decrements, those are applied to the latest data, so even if users are editing properties of the same model, their changes will stack. This functionality is designed to accommodate scenarios where users may be cataloging devices of the same model but not the exact same item simultaneously (that would be physically impossible). Additionally, the app automatically refreshes the data every 30 seconds during periods of idling to ensure all users are viewing to the latest information.
- **Admin Authentication**: To make any changes to the data, you must be authenticated. The app uses the Sodium library for secure password hashing. User passwords are hashed and compared against pre-stored hashes in a secure JSON file (`confidential/shinypasswords.json`). To align with the Streamlit application, this implementation has two possible passwords, either giving the same access in the Shiny application. To authenicate, either click the button or hit Enter.
- **Download Data**: Option to download the current inventory data as a CSV file.
- **Item Merging**: Automatically collapses items with the same name and comments, even if they are tagged in different sections, simplifying data entry and decluttering the table. Even if the data started with duplicates, when trying to add another of the item, the app will automatically collapse them into a single line item with summed quantity. This detection of identical elements is thorough - eliminating more than one consecutive space, extra white space, or case differences.
- **Flexible Initial Data**: The initial Google Sheet can either have an Estimated Price column or not: the app will work either way. If it does not have it, it will never prompt you to enter a price for the item or display the column in the future in the data table.  

## Getting Started

## Installation
Install the required packages:
```R
install.packages(c("shiny", "tidyverse", "plotly", "DT", "shinyjs", "sodium", "googlesheets4"))
```

## Configuration
To set up the Shiny app, you need to configure the service account integration with Google Sheets as well as the SHA-256 password hashes for authentication.

### Google Sheets Integration

Fill out the `confidential/hhinventory_service_account_credentials.json` file with your Google service account credentials. For instructions, see the [Service Account Setup Guide](service_account_help.md). Below is a template of what the file should look like:

```json
{
  "type": "service_account",
  "project_id": "your_project_id",
  "private_key_id": "your_private_key_id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nyour_private_key\n-----END PRIVATE KEY-----\n",
  "client_email": "your_service_account_email@your_project_id.iam.gserviceaccount.com",
  "client_id": "your_client_id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email@your_project_id.iam.gserviceaccount.com"
}
```


### Authentication Setup

Store your SHA-256 password hashes in the `confidential/shinypasswords.json` file. Below is a template of what the file should look like:

```json
{
  "admin_passwords": {
    "hash1": "your_first_hashed_password",
    "hash2": "your_second_hashed_password"
  }
}
```

#### Hashing Passwords
Use the following R script to hash your passwords:
```r
library(sodium)

hash_password <- function(password) {
  hashed <- sodium::password_store(password)
  return(hashed)
}

password1 <- "your_first_password"
password2 <- "your_second_password"

hashed_password1 <- hash_password(password1)
hashed_password2 <- hash_password(password2)

cat("Hashed Password 1:", hashed_password1, "\n")
cat("Hashed Password 2:", hashed_password2, "\n")
```

## Using the App
Open the app.R file in RStudio.
Run the application by clicking the "Run App" button in RStudio or by using the command:
```R
shiny::runApp()
```

### Deployment

Install and load the rsconnect Package into your R session:
```R
install.packages("rsconnect")
library(rsconnect)
```

Use the `rsconnect` package to authenticate your shinyapps.io account:
```R
rsconnect::setAccountInfo(name='your_shinyapps_username', 
                          token='your_token', 
                          secret='your_secret')
```

Deploy the app to shinyapps.io:
```R
rsconnect::deployApp()
```

Or more generally:
```R
rsconnect::deployApp('path_to_your_app_directory')
```

## Current Issues
- **State Resetting**: When updating the data table, the state (e.g., current page, search filters) resets. This can be inconvenient for users making multiple edits. Considerations for improvement include maintaining state between updates.

## Future Enhancements
- Adding features such as time-based notifications, change history, and the ability to update item sections or item prices.

# Scripts
Additionally in the repository, there are several scripts included in the project that can perform the following tasks:
- Estimate the price of phone models based on predefined criteria.
- Use a language model to generate price estimates for phone models. The GPT-2 model runs locally and provides a free method for estimating prices without the same casework and predefined criteria, but as it is a text-generation model without real-time data, it is very inaccurate.
- Merge data from different CSV files to create a comprehensive dataset of billing and subscription information.
