# Harvest Hope Inventory Management Shiny App

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
