library(shiny)
library(tidyverse)
library(plotly)
library(DT)
library(shinyjs)
library(googlesheets4)

# Service account
gs4_auth(path = "confidential/hhinventory_service_account_credentials.json")

# Google Sheet ID and Sheet Name with data
sheet_id <- "1hFROHxAvUrZKADr1H7fY2RGWH4I0LeXKCoqux7tObqw"
sheet_name <- "ServerSandbox"

# Function to read inventory data from Google Sheet and create Combined_Section
read_inventory <- function() {
  inventory <- read_sheet(sheet_id, sheet = sheet_name) %>%
    mutate(Combined_Section = case_when(
      Section %in% c("Laptops", "Laptop Chargers", "Laptop Batteries", "Laptop Accessories") ~ "Laptops & Accessories",
      Section %in% c("Tablets", "Tablet Chargers", "Tablet Cases and Accessories") ~ "Tablets & Accessories",
      Section %in% c("Phones", "Phone Cases") ~ "Phones & Accessories",
      Section %in% c("Networking Equipment", "Access Points") ~ "Networking Equipment",
      Section %in% c("Storage Devices") ~ "Storage Devices",
      Section %in% c("Printers and Scanners") ~ "Printers & Scanners",
      Section %in% c("Audio and Video Equipment") ~ "Audio & Video Equipment",
      Section %in% c("Cables and Adapters") ~ "Cables & Adapters",
      Section %in% c("Computer Peripherals", "Monitors", "TVs") ~ "Peripherals & Displays",
      Section %in% c("Miscellaneous Tech", "Other Accessories") ~ "Miscellaneous & Accessories",
      TRUE ~ Section
    ))
  return(inventory)
}

ui <- fluidPage(
  useShinyjs(),
  titlePanel("Inventory Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sections", "Select Sections:", choices = NULL, selected = NULL),
      hr(),
      helpText("Data visualization and interactive table for inventory management."),
      hr(),
      textInput("item_name", "Item:", ""),
      numericInput("item_quantity", "Quantity:", 1, min = 1),
      textInput("item_comment", "Comment:", ""),
      selectInput("item_section", "Section:", choices = NULL),
      actionButton("add_item", "Add Item"),
      hr(),
      conditionalPanel(
        condition = "!output.admin_status",
        passwordInput("admin_password", "Admin Password:"),
        actionButton("admin_login", "Admin Login")
      ),
      hr(),
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
    inventory <- tryCatch({
      read_inventory()
    }, error = function(e) {
      showNotification(paste("Failed to read data:", e$message), type = "error")
      NULL
    })
    if (!is.null(inventory)) {
      inventory_data(inventory)
      updateCheckboxGroupInput(session, "sections", choices = unique(inventory$Combined_Section), selected = unique(inventory$Combined_Section))
      updateSelectInput(session, "item_section", choices = unique(inventory$Section))
    }
  })
  
  admin_status <- reactiveVal(FALSE)
  
  observeEvent(input$admin_login, {
    # Hashed password should be securely stored and managed
    hashed_password <- "$7$C6..../....LbSHcf7gGddIJ8ePwquEtXywH3rAGBhs3O9I/NWz60/$SFFJkNa1XLPXFYqEXqOADzRLb9huyw/KlRO5Fc7KjY8"
    if (sodium::password_verify(hashed_password, input$admin_password)) {
      admin_status(TRUE)
      showNotification("Logged in as admin.", type = "message")
    } else {
      showNotification("Incorrect password.", type = "error")
    }
  })
  
  output$barPlot <- renderPlotly({
    req(inventory_data())
    data <- inventory_data() %>%
      group_by(Combined_Section) %>%
      summarise(Total_Quantity = sum(Quantity, na.rm = TRUE), .groups = 'drop')
    
    plot_ly(data, x = ~Combined_Section, y = ~Total_Quantity, type = 'bar', color = ~Combined_Section) %>%
      layout(title = 'Total Quantity of Items by Combined Section', xaxis = list(title = 'Combined Section'), yaxis = list(title = 'Total Quantity'))
  })
  
  output$dataTable <- renderDT({
    datatable(inventory_data(), options = list(pageLength = 10, autoWidth = TRUE), class = "display")
  }, server = TRUE)
  
  output$admin_status <- reactive({ admin_status() })
  outputOptions(output, 'admin_status', suspendWhenHidden = FALSE)
  
  output$downloadData <- downloadHandler(
    filename = function() {
      paste("inventory-", Sys.Date(), ".csv", sep="")
    },
    content = function(file) {
      write_csv(inventory_data(), file)
    }
  )
}

# Run the app
shinyApp(ui = ui, server = server)
