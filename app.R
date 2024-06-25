# Version of Shiny App with Google Sheets Integration (not CSV)
library(shiny)
library(tidyverse)
library(plotly)
library(DT)
library(shinyjs)
library(googlesheets4)
library(sodium)
library(jsonlite)

# Authentication and setup
gs4_auth(path = "confidential/hhinventory_service_account_credentials.json")

# Google Sheet settings
sheet_id <- "1hFROHxAvUrZKADr1H7fY2RGWH4I0LeXKCoqux7tObqw"
sheet_name <- "testcompat"

# Password hashes to check against for authentication
hashes <- fromJSON("confidential/shinypasswords.json")

# Read and prepare inventory data
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
    )) %>%
    mutate(RowID = row_number())  # For internal use only; not displayed
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
      conditionalPanel(
        condition = "!output.admin_status",
        passwordInput("admin_password", "Admin Password:"),
        actionButton("admin_login", "Admin Login")
      ),
      downloadButton("downloadData", "Download CSV")
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      actionButton("show_quantity", "Show Quantity", class = "btn-primary"),
      actionButton("show_price", "Show Total Price", class = "btn-info"),
      DTOutput("dataTable"),
      tags$style(HTML("
        .dataTables_wrapper {
          width: 100% !important; 
          height: 100%;
        }
        .dataTables_scrollBody {
          width: 100% !important;
        }
        table.dataTable {
          width: 100% !important;
        }
        .btn-primary, .btn-info {
          width: 49%; 
          margin: 5px 1% 20px 1%;
        }
      "))
    )
  )
)



server <- function(input, output, session) {
  # Securely stored hashed password (pre-hashed using sodium::password_store)
  hashed_password1 <- hashes$admin_passwords$hash1
  hashed_password2 <- hashes$admin_passwords$hash2
  inventory_data <- reactiveVal()
  
  observe({
    invalidateLater(30000, session)  # Refresh data every 30 seconds to keep it fresh from concurrent modifications
    inventory <- read_inventory() # Adding, removing, etc all do not need this functionality - they pull the latest right before they write
    inventory_data(inventory) # This is mainly for extensive idle time
    updateCheckboxGroupInput(session, "sections", choices = unique(inventory$Combined_Section), selected = unique(inventory$Combined_Section))
    updateSelectInput(session, "item_section", choices = unique(inventory$Section))
  })
  
  admin_status <- reactiveVal(FALSE)
  
  observeEvent(input$admin_login, {
    if (sodium::password_verify(hashed_password1, input$admin_password) | sodium::password_verify(hashed_password2, input$admin_password)) {
      admin_status(TRUE)
      showNotification("Logged in as admin.", type = "message")
    } else {
      showNotification("Incorrect password.", type = "error")
    }
  })
  
  observeEvent(input$add_item, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to add items.", type = "error")
      return()
    }    
    
    current_inventory <- read_inventory() #default
    
    new_item <- tibble(
      Item = input$item_name,
      Quantity = input$item_quantity,
      Comments = input$item_comment,
      Section = input$item_section,
      Combined_Section = case_when(
        input$item_section %in% c("Laptops", "Laptop Chargers", "Laptop Batteries", "Laptop Accessories") ~ "Laptops & Accessories",
        input$item_section %in% c("Tablets", "Tablet Chargers", "Tablet Cases and Accessories") ~ "Tablets & Accessories",
        input$item_section %in% c("Phones", "Phone Cases") ~ "Phones & Accessories",
        input$item_section %in% c("Networking Equipment", "Access Points") ~ "Networking Equipment",
        input$item_section %in% c("Storage Devices") ~ "Storage Devices",
        input$item_section %in% c("Printers and Scanners") ~ "Printers & Scanners",
        input$item_section %in% c("Audio and Video Equipment") ~ "Audio & Video Equipment",
        input$item_section %in% c("Cables and Adapters") ~ "Cables & Adapters",
        input$item_section %in% c("Computer Peripherals", "Monitors", "TVs") ~ "Peripherals & Displays",
        input$item_section %in% c("Miscellaneous Tech", "Other Accessories") ~ "Miscellaneous & Accessories",
        TRUE ~ input$item_section
      ),
      RowID = max(current_inventory$RowID, na.rm = TRUE) + 1
    )
    
    updated_inventory <- bind_rows(current_inventory, new_item) %>%
      group_by(Item, Comments) %>%
      summarise(Quantity = sum(Quantity, na.rm = TRUE), Section = first(Section), Combined_Section = first(Combined_Section), RowID = first(RowID), .groups = 'drop')
    
    inventory_data(updated_inventory)
    write_inventory(updated_inventory)
    
    replaceData(dataTableProxy, updated_inventory, resetPaging = FALSE)
  })
  
  output$dataTable <- renderDT({
    datatable(
      inventory_data() %>%
        mutate(Quantity = sprintf(
          '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
          Quantity, RowID, RowID
        )) %>%
        select(-RowID, -Combined_Section),
      escape = FALSE,
      options = list(
        pageLength = 10,
        autoWidth = FALSE,
        stateSave = TRUE,
        scrollX = TRUE,
        scrollY = 'calc(100vh - 250px)',
        columnDefs = list(
          list(width = '150px', targets = 3), 
          list(className = 'dt-center', targets = "_all")
        )
      )
    )
  }, server = TRUE)
  
  dataTableProxy <- dataTableProxy('dataTable')
  
  observe({
    shinyjs::runjs("
    $(document).on('click', 'button[id^=plus_]', function() {
      var id = $(this).attr('id'); 
      Shiny.setInputValue('plus_button', id, {priority: 'event'});
    });
    
    $(document).on('click', 'button[id^=minus_]', function() {
      var id = $(this).attr('id');
      Shiny.setInputValue('minus_button', id, {priority: 'event'});
    });
  ")
  })
  
  observeEvent(input$plus_button, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to modify items.", type = "error")
      return()
    }    
    plus_index <- as.numeric(sub("plus_", "", input$plus_button))
    updated_inventory <- read_inventory()
    
    target_row <- which(updated_inventory$RowID == plus_index)
    updated_inventory$Quantity[target_row] <- updated_inventory$Quantity[target_row] + 1    
    
    inventory_data(updated_inventory)
    write_inventory(updated_inventory)
    
    replaceData(dataTableProxy, updated_inventory, resetPaging = FALSE)
  })
  
  observeEvent(input$minus_button, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to modify items.", type = "error")
      return()
    }    
    minus_index <- as.numeric(sub("minus_", "", input$minus_button))
    updated_inventory <- read_inventory()
    
    target_row <- which(updated_inventory$RowID == minus_index)
    updated_inventory$Quantity[target_row] <- updated_inventory$Quantity[target_row] - 1
    
    if (updated_inventory$Quantity[target_row] <= 0) {
      updated_inventory <- updated_inventory[-target_row, ]
    }
    
    inventory_data(updated_inventory)
    write_inventory(updated_inventory)
    
    replaceData(dataTableProxy, updated_inventory, resetPaging = FALSE)
  })
  
  plot_type <- reactiveVal("quantity")  #default
  
  observeEvent(input$show_quantity, {
    plot_type("quantity")
  })
  
  observeEvent(input$show_price, {
    plot_type("price")
  })
  
  output$barPlot <- renderPlotly({
    data <- inventory_data()
    if (plot_type() == "quantity") {
      data_summarized <- data %>%
        group_by(Combined_Section) %>%
        summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
      plot_ly(data_summarized, x = ~Combined_Section, y = ~Total_Quantity, type = 'bar') %>%
        layout(
          title = 'Total Quantity of Items by Section',
          xaxis = list(title = 'Combined Section'),
          yaxis = list(title = 'Total Quantity')
        )
    } else {
      data_summarized <- data %>%
        group_by(Combined_Section) %>%
        summarise(Total_Price = sum(Quantity * `Estimated Price`, na.rm = TRUE))
      plot_ly(data_summarized, x = ~Combined_Section, y = ~Total_Price, type = 'bar', marker = list(color = 'rgb(50, 171, 96)')) %>%
        layout(
          title = 'Total Price of Items by Section',
          xaxis = list(title = 'Combined Section'),
          yaxis = list(title = 'Total Price', tickprefix = "$")
        )
    }
  })
  
  
  output$admin_status <- reactive({
    admin_status()
  })
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

shinyApp(ui = ui, server = server)