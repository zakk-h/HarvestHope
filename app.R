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
    mutate(
      Combined_Section = case_when(
        Section %in% c(
          "Laptops",
          "Laptop Chargers",
          "Laptop Batteries",
          "Laptop Accessories"
        ) ~ "Laptops & Accessories",
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
      )
    ) %>%
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
      numericInput("item_price", "Price:", value = NA, min = 0, step = 1),
      textInput("item_comment", "Comment:", ""),
      selectInput("item_section", "Section:", choices = NULL),
      actionButton("add_item", "Add Item"),
      conditionalPanel(
        # Goes away once authenticated
        condition = "!output.admin_status",
        passwordInput("admin_password", "Admin Password:"),
        actionButton("admin_login", "Admin Login")
      ),
      downloadButton("downloadData", "Download CSV")
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      # Navigation buttons between two plots
      div(
        style = "text-align: center; margin-top: 5px;",
        actionLink(
          "show_quantity",
          label = "",
          icon = icon("circle"),
          class = "plot-nav-button blue"
        ),
        actionLink(
          "show_price",
          label = "",
          icon = icon("circle"),
          class = "plot-nav-button gray"
        )
      ),
      DTOutput("dataTable"),
      # Data table must fill space horizontally
      tags$style(
        HTML(
          "
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
        .plot-nav-button {
          font-size: 10px;
          font-weight: bold;
          padding: 0 5px;
          vertical-align: middle;
          text-decoration: none !important; /* No underlining from hyperlinks */
        }
        .plot-nav-button.blue {
          color: #007BFF;
        }
        .plot-nav-button.gray {
          color: #6c757d;
        }
      "
        )
      )
    )
  )
)

server <- function(input, output, session) {
  
  inventory_data <- reactiveVal()
  
  # Load inventory initially and store in reactive value
  initial_inventory <- read_inventory()
  inventory_data(initial_inventory)
  
  # Check if "Estimated Price" exists and adjust UI accordingly
  if ("Estimated Price" %in% names(initial_inventory)) {
    shinyjs::show("item_price")
    show_estimated_price = TRUE
  } else {
    shinyjs::hide("item_price")
    show_estimated_price = FALSE
  }
  
  
  # Define initial sections and selections based on the first data load
  sections <- unique(initial_inventory$Combined_Section)
  selections <- sections  # Default to selecting all sections initially
  
  # Update the UI elements for sections and item section selection
  updateCheckboxGroupInput(
    session,
    "sections",
    choices = sections,
    selected = selections
  )
  
  updateSelectInput(
    session,
    "item_section",
    choices = unique(initial_inventory$Section)
  )
  
  # Securely stored hashed password (pre-hashed using sodium::password_store)
  hashed_password1 <- hashes$admin_passwords$hash1
  hashed_password2 <- hashes$admin_passwords$hash2
  
  observe({
    invalidateLater(30000, session)  # Refresh data every 30 seconds to keep it fresh from concurrent modifications
    
    inventory <-
      read_inventory() # Adding, removing, etc all do not need this functionality - they pull the latest right before they write
    inventory_data(inventory) # This is mainly for extensive idle time
    
    # Updating inventory_data will trigger the data table to update, etc.
  })
  
  admin_status <-
    reactiveVal(FALSE) # Default reactive val, run only at startup
  
  observeEvent(input$admin_login, {
    # Action button trigger
    # This implementation allows two passwords (with the same level of authentication: write access)
    if (sodium::password_verify(hashed_password1, input$admin_password) |
        sodium::password_verify(hashed_password2, input$admin_password)) {
      admin_status(TRUE) # Will hide password prompt now because of conditional UI
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
    
    current_inventory <-
      read_inventory() # Getting fresh data from the Google Sheet
    
    new_item <- tibble(
      Item = input$item_name,
      Quantity = input$item_quantity,
      Comments = input$item_comment,
      Section = input$item_section,
      Combined_Section = case_when(
        # Combined Section for visualization
        input$item_section %in% c(
          "Laptops",
          "Laptop Chargers",
          "Laptop Batteries",
          "Laptop Accessories"
        ) ~ "Laptops & Accessories",
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
      `Estimated Price` = ifelse("Estimated Price" %in% names(current_inventory), input$item_price, NA),
      RowID = max(current_inventory$RowID, na.rm = TRUE) + 1 # The next row id; this itself doesn't mean it goes last, it just gives a unique identifier. There will never be a gap because the row id assigned to the imported data is the row number from the sheet which is assumed to be continuous.
    )
    
    # Binding new_item as the row following the end of current_inventory
    # Could swap parameters to make new_item be added to the front/top
    updated_inventory <- bind_rows(current_inventory, new_item) %>%
      group_by(Item, Comments) %>%
      summarise(
        Quantity = sum(Quantity, na.rm = TRUE),
        Section = first(Section),
        Combined_Section = first(Combined_Section),
        `Estimated Price` = first(`Estimated Price`),
        RowID = first(RowID),
        .groups = 'drop'
      )
    
    # Removing estimated_price column if it wasn't there originally
    if (!show_estimated_price) {
      updated_inventory <- select(updated_inventory, -`Estimated Price`)
    }
    
    inventory_data(updated_inventory) # Keeping reactive value updated
    write_inventory(updated_inventory) # Writing back to Google Sheet
    
    replaceData(dataTableProxy, updated_inventory, resetPaging = FALSE) # Updating what is displayed in the data table
  })
  
  # Rendering of the data table - will rerun whenever a dependency changes - such as sections checked or the data
  output$dataTable <- renderDT({
    datatable(
      # Only display the sections checked in checkboxGroupInput
      filtered_data <- inventory_data() %>%
        filter(Combined_Section %in% input$sections) %>%
        mutate(
          Quantity = sprintf(
            # Quantity column to include the quantity and buttons
            '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
            Quantity,
            RowID,
            RowID
          )
        ) %>%
        select(-RowID,-Combined_Section),
      # Not worth displaying
      escape = FALSE,
      options = list(
        pageLength = 10,
        autoWidth = FALSE,
        stateSave = FALSE,
        # Not working reliably
        scrollX = TRUE,
        scrollY = 'calc(100vh - 250px)',
        columnDefs = list(
          list(width = '150px', targets = 3),
          # Setting width of 4th column (index 3) - the column with buttons
          list(className = 'dt-center', targets = "_all") # Centers text
        )
      )
    )
  }, server = TRUE) # Server side processing
  
  dataTableProxy <- dataTableProxy('dataTable')
  
  # jQuery listens for clicks for buttons that start with plus_ or minus_ and sets input value accordingly so it can be observed and handled at the correct row
  observe({
    shinyjs::runjs(
      "
    $(document).on('click', 'button[id^=plus_]', function() {
      var id = $(this).attr('id');
      Shiny.setInputValue('plus_button', id, {priority: 'event'});
    });

    $(document).on('click', 'button[id^=minus_]', function() {
      var id = $(this).attr('id');
      Shiny.setInputValue('minus_button', id, {priority: 'event'});
    });
  "
    )
  })
  
  # input detected from the above js.
  observeEvent(input$plus_button, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to modify items.", type = "error")
      return()
    }
    # extract row number
    plus_index <- as.numeric(sub("plus_", "", input$plus_button))
    updated_inventory <- read_inventory()
    
    # find target row
    target_row <- which(updated_inventory$RowID == plus_index)
    updated_inventory$Quantity[target_row] <-
      updated_inventory$Quantity[target_row] + 1
    
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
    updated_inventory$Quantity[target_row] <-
      updated_inventory$Quantity[target_row] - 1
    
    if (updated_inventory$Quantity[target_row] <= 0) {
      updated_inventory <- updated_inventory[-target_row,]
    }
    
    inventory_data(updated_inventory)
    write_inventory(updated_inventory)
    
    replaceData(dataTableProxy, updated_inventory, resetPaging = FALSE)
  })
  
  plot_type <- reactiveVal("quantity")  #default
  
  observeEvent(input$show_quantity, {
    # Updating reactive value
    plot_type("quantity")
    # Removing the additional class (color), leaving the base (button)
    # Swapping colors to show which is active
    shinyjs::removeClass(selector = "#show_price", class = "blue")
    shinyjs::addClass(selector = "#show_price", class = "gray")
    shinyjs::removeClass(selector = "#show_quantity", class = "gray")
    shinyjs::addClass(selector = "#show_quantity", class = "blue")
  })
  
  observeEvent(input$show_price, {
    plot_type("price")
    shinyjs::removeClass(selector = "#show_quantity", class = "blue")
    shinyjs::addClass(selector = "#show_quantity", class = "gray")
    shinyjs::removeClass(selector = "#show_price", class = "gray")
    shinyjs::addClass(selector = "#show_price", class = "blue")
  })
  
  # Render bar plot and will rerun whenever plot_type or inventory_data or input$sections (reactive expressions or inputs) change - they are dependencies
  output$barPlot <- renderPlotly({
    # Only display the sections checked in checkboxGroupInput
    filtered_data <- inventory_data() %>%
      filter(Combined_Section %in% input$sections)
    if (plot_type() == "quantity") {
      data_summarized <- filtered_data %>%
        group_by(Combined_Section) %>%
        summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
      plot_ly(
        data_summarized,
        x = ~ Combined_Section,
        y = ~ Total_Quantity,
        type = 'bar'
      ) %>%
        layout(
          title = 'Total Quantity of Items by Section',
          xaxis = list(title = 'Combined Section'),
          yaxis = list(title = 'Total Quantity')
        )
    } else {
      if (!"Estimated Price" %in% names(filtered_data)) {
        # Return a plotly object with a message instead of a plot
        plot_ly() %>%
          add_annotations(
            text = "The 'Estimated Price' data is not available.",
            x = 0.5,
            y = 0.5,
            xref = 'paper',
            yref = 'paper',
            showarrow = FALSE,
            font = list(
              family = "Arial",
              size = 16,
              color = "red"
            )
          ) %>%
          layout(
            xaxis = list(showticklabels = FALSE),
            yaxis = list(showticklabels = FALSE)
          )
      } else {
        data_summarized <- filtered_data %>%
          group_by(Combined_Section) %>%
          summarise(Total_Price = sum(Quantity * `Estimated Price`, na.rm = TRUE))
        plot_ly(
          data_summarized,
          x = ~ Combined_Section,
          y = ~ Total_Price,
          type = 'bar',
          marker = list(color = 'rgb(50, 171, 96)')
        ) %>%
          layout(
            title = 'Total Price of Items by Section',
            xaxis = list(title = 'Combined Section'),
            yaxis = list(title = 'Total Price', tickprefix = "$")
          )
      }
      
    }
  })
  
  output$admin_status <- reactive({
    admin_status()
  })
  outputOptions(output, 'admin_status', suspendWhenHidden = FALSE) # Need suspendWhenHidden to be false to remove the UI elements, otherwise, it would already be suspended before removing
  
  # Download as csv, only runs when clicked
  output$downloadData <- downloadHandler(
    # Datestamped filename
    filename = function() {
      paste("inventory-", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write_csv(inventory_data(), file)
    }
  )
}

shinyApp(ui = ui, server = server)