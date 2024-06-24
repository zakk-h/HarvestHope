#### Creating a Service Account

1. **Create a Google Cloud Project**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing project.

2. **Enable the Google Sheets API**:
    - In the Google Cloud Console, navigate to the "APIs & Services" dashboard.
    - Click on "Enable APIs and Services" and search for "Google Sheets API".
    - Enable the Google Sheets API for your project.

3. **Create a Service Account**:
    - Go to "APIs & Services" > "Credentials".
    - Click on "Create Credentials" and select "Service Account".
    - Fill in the required details and create the service account.
    - Go to the service account you created, and under the "Keys" section, add a new key of type "JSON". Download the JSON file.

4. **Share the Google Sheet**:
    - Open the Google Sheet you want to integrate with.
    - Share it with the client email from the JSON key file (e.g., `your-service-account@your-project-id.iam.gserviceaccount.com`).

#### Storing the Service Account Credentials

Save the downloaded JSON file to the `confidential` directory in your project.

For the Shiny app, rename it to `hhinventory_service_account_credentials.json`.

For the Streamlit app, convert the JSON content to TOML format and place it in the `.streamlit/secrets.toml` file under the `[gcp_service_account]` section.


### 2. Authentication Setup