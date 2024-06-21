library(shiny)
library(tidyverse)
library(plotly)
library(DT)
library(shinyjs)
library(googlesheets4)
library(sodium)

# Authentication and setup
gs4_auth(path = "confidential/hhinventory_service_account_credentials.json")

# Google Sheet settings
sheet_id <- "1hFROHxAvUrZKADr1H7fY2RGWH4I0LeXKCoqux7tObqw"
sheet_name <- "ServerSandbox"

# Read and prepare inventory data
read_inventory <- function() {
  inventory <- read_sheet(sheet_id, sheet = sheet_name) %>%
    mutate(Combined_Section = case_when(
      Section %in% c("Laptops", "Laptop Chargers", "Laptop Batteries", "Laptop Accessories") ~ "Laptops & Accessories",
      # Add other sections accordingly
      TRUE ~ Section
    )) %>%
    mutate(RowID = row_number())  # This is for internal use
  return(inventory)
}

# Write data to Google Sheet
write_inventory <- function(inventory_df) {
  sheet_write(inventory_df, sheet_id, sheet = sheet_name)
}

ui <- fluidPage(
  useShinyjs(),
  titlePanel("Inventory Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sections", "Select Sections:", choices = NULL),
      textInput("item_name", "Item:", ""),
      numericInput("item_quantity", "Quantity:", 1, min = 1),
      textInput("item_comment", "Comment:", ""),
      selectInput("item_section", "Section:", choices = NULL),
      actionButton("add_item", "Add Item"),
      passwordInput("admin_password", "Admin Password:"),
      actionButton("admin_login", "Admin Login"),
      downloadButton("downloadData", "Download CSV")
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      DTOutput("dataTable")
    )
  )
)

server <- function(input, output, session) {
  inventory_data <- reactiveVal()
  
  observe({
    invalidateLater(30000, session)  # Refresh data every 30 seconds
    inventory <- read_inventory()
    inventory_data(inventory)
    updateCheckboxGroupInput(session, "sections", choices = unique(inventory$Combined_Section), selected = unique(inventory$Combined_Section))
    updateSelectInput(session, "item_section", choices = unique(inventory$Section))
  })
  
  admin_status <- reactiveVal(FALSE)
  
  observeEvent(input$admin_login, {
    # Placeholder for real hashed password check
    admin_status(TRUE)
  })
  
  observeEvent(input$add_item, {
    if (!admin_status()) return()
    
    new_item <- tibble(
      Item = input$item_name,
      Quantity = input$item_quantity,
      Comments = input$item_comment,
      Section = input$item_section
    )
    # Update inventory
    updated_inventory <- bind_rows(inventory_data(), new_item)
    inventory_data(updated_inventory)
    write_inventory(updated_inventory)
  })
  
  output$dataTable <- renderDT({
    datatable(inventory_data(), escape = FALSE, selection = 'none', options = list(
      dom = 'Bfrtip',
      buttons = c('copy', 'csv', 'excel', 'pdf', 'print'),
      paging = TRUE,
      searching = TRUE
    ))
  }, server = TRUE)
  
  output$barPlot <- renderPlotly({
    data <- inventory_data() %>%
      group_by(Combined_Section) %>%
      summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
    plot_ly(data, x = ~Combined_Section, y = ~Total_Quantity, type = 'bar') %>%
      layout(title = 'Total Quantity of Items by Section')
  })
  
  output$downloadData <- downloadHandler(
    filename = function() {
      paste("inventory-", Sys.Date(), ".csv", sep="")
    },
    content = function(file) {
      write_csv(inventory_data(), file)
    }
  )
}

shinyApp(ui = ui, server = server)
