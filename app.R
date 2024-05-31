library(shiny)
library(tidyverse)
library(plotly)
library(DT)
library(shinyjs)
library(sodium)

inventory <- read_csv("TechInventory.csv")

inventory_combined <- inventory %>%
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
    TRUE ~ Section # Else, label them as they already were
  ))

colors <- c("deepskyblue", "mediumpurple", "plum", "forestgreen", "orange", "orchid", "gold", "lightcoral", "blueviolet", "darkorchid")

ui <- fluidPage(
  useShinyjs(),
  titlePanel("Inventory Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sections", "Select Sections:", 
                         choices = unique(inventory_combined$Combined_Section), 
                         selected = unique(inventory_combined$Combined_Section)),
      hr(),
      helpText("Data visualization and interactive table for inventory management."),
      hr(),
      textInput("item_name", "Item:", ""),
      numericInput("item_quantity", "Quantity:", 1, min = 1),
      textInput("item_comment", "Comment:", ""),
      selectInput("item_section", "Section:", choices = unique(inventory_combined$Section)),
      actionButton("add_item", "Add Item"),
      hr(),
      conditionalPanel(
        condition = "!output.admin_status",
        passwordInput("admin_password", "Admin Password:"),
        actionButton("admin_login", "Admin Login")
      ),
      hr()
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      DTOutput("dataTable")
    )
  )
)

server <- function(input, output, session) {
  # Securely stored hashed password (pre-hashed using sodium::password_store)
  hashed_password <- "$7$C6..../....LbSHcf7gGddIJ8ePwquEtXywH3rAGBhs3O9I/NWz60/$SFFJkNa1XLPXFYqEXqOADzRLb9huyw/KlRO5Fc7KjY8"
  
  # Only user selections
  filtered_data <- reactive({
    inventory_combined %>%
      filter(Combined_Section %in% input$sections)
  })
  
  # Only run the first initial time, inventory_combined doesn't change
  inventory_data <- reactiveVal(inventory_combined)
  
  # Admin status
  admin_status <- reactiveVal(FALSE)
  
  # Authenticate admin by comparing created hash
  observeEvent(input$admin_login, {
    if (sodium::password_verify(hashed_password, input$admin_password)) {
      admin_status(TRUE)
      showNotification("Logged in as admin.", type = "message")
    } else {
      showNotification("Incorrect password.", type = "error")
    }
  })
  
  filtered_data <- reactive({
    req(inventory_data()) 
    inventory_data() %>%
      filter(Combined_Section %in% input$sections) # Based on user selected sections
  })
  
  # Add item to inventory
  observeEvent(input$add_item, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to add items.", type = "error")
      return()
    }
    
    new_item <- tibble(
      Item = str_trim(input$item_name),
      Quantity = input$item_quantity,
      Comments = str_trim(input$item_comment),
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
      )
    )
    
    # If the user tries to add an item with the same name and set of comments, merge them
    # Usually comments would be blank. If they have different comments, they should be kept separate
    # Even if these items have different sections, we accept this as a user mistake and still merge, because they have the same item name
    # In the case of different sections, they merge into the first (existing) category.
    updated_inventory <- bind_rows(inventory_data(), new_item) %>%
      group_by(Item, Comments) %>%
      summarise(Quantity = sum(Quantity, na.rm = TRUE), Section = first(Section), Combined_Section = first(Combined_Section), .groups = 'drop')
    inventory_data(updated_inventory)
    
    write_csv(updated_inventory, "TechInventory.csv")
    
    output$dataTable <- renderDT({
      datatable(
        filtered_data() %>%
          select(-Combined_Section) %>%
          mutate(Quantity = sprintf(
            '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
            Quantity, row_number(), row_number()
          )),
        escape = FALSE,
        options = list(
          pageLength = 10,
          stateSave = TRUE,
          autoWidth = FALSE,
          columnDefs = list(
            list(width = '150px', targets = 4),  # 5th column, adjusting + - column
            list(className = 'dt-center', targets = "_all")
          )
        )
      )
    }, server = FALSE)
    
    
    showNotification("Item added to the inventory.", type = "message")
  })
  
  # Initially render bar plot
  output$barPlot <- renderPlotly({
    data <- inventory_data() %>%
      group_by(Combined_Section) %>%
      summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
    
    plot_ly(data, x = ~reorder(Combined_Section, -Total_Quantity), y = ~Total_Quantity, type = 'bar', color = ~Combined_Section, colors = colors) %>%
      layout(title = 'Total Quantity of Items by Combined Section',
             xaxis = list(title = 'Combined Section'),
             yaxis = list(title = 'Total Quantity'))
  })
  
  # Initially render data table with plus and minus buttons
  output$dataTable <- renderDT({
    datatable(
      filtered_data() %>%
        select(-Combined_Section) %>%
        mutate(Quantity = sprintf(
          '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
          Quantity, row_number(), row_number()
        )),
      escape = FALSE,
      options = list(
        pageLength = 10,
        autoWidth = FALSE,  
        columnDefs = list(
          list(width = '150px', targets = 4), 
          list(className = 'dt-center', targets = "_all")
        )
      )
    )
  }, server = FALSE)
  
  # Shinyjs to add JavaScript for handling button clicks
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
  
  # Handle plus button click
  observeEvent(input$plus_button, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to modify items.", type = "error")
      return()
    }    
    plus_index <- as.numeric(sub("plus_", "", input$plus_button))
    updated_inventory <- inventory_data()
    updated_inventory$Quantity[plus_index] <- updated_inventory$Quantity[plus_index] + 1
    inventory_data(updated_inventory)
    
    write_csv(updated_inventory, "TechInventory.csv")
    
    # Refresh the data table
    output$dataTable <- renderDT({
      datatable(
        filtered_data() %>%
          select(-Combined_Section) %>%
          mutate(Quantity = sprintf(
            '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
            Quantity, row_number(), row_number()
          )),
        escape = FALSE,
        options = list(
          pageLength = 10,
          stateSave = TRUE,
          autoWidth = FALSE,  
          columnDefs = list(
            list(width = '150px', targets = 4), 
            list(className = 'dt-center', targets = "_all")
          )
        )
      )
    }, server = FALSE)
  })
  
  # Handle minus button click
  observeEvent(input$minus_button, {
    if (!admin_status()) {
      showNotification("Error: You do not have admin rights to modify items.", type = "error")
      return()
    }    
    minus_index <- as.numeric(sub("minus_", "", input$minus_button))
    updated_inventory <- inventory_data()
    updated_inventory$Quantity[minus_index] <- updated_inventory$Quantity[minus_index] - 1
    
    # Remove item if quantity reaches 0
    if (updated_inventory$Quantity[minus_index] <= 0) {
      updated_inventory <- updated_inventory[-minus_index, ]
    }
    
    inventory_data(updated_inventory)
    
    write_csv(updated_inventory, "TechInventory.csv")
    
    # Refresh the data table
    output$dataTable <- renderDT({
      datatable(
        filtered_data() %>%
          select(-Combined_Section) %>%
          mutate(Quantity = sprintf(
            '%s <div style="white-space: nowrap;"><button id="minus_%s" class="btn btn-secondary btn-sm">-</button> <button id="plus_%s" class="btn btn-secondary btn-sm">+</button></div>',
            Quantity, row_number(), row_number()
          )),
        escape = FALSE,
        options = list(
          pageLength = 10,
          stateSave = TRUE,
          autoWidth = FALSE, 
          columnDefs = list(
            list(width = '150px', targets = 4),  # 5th column
            list(className = 'dt-center', targets = "_all")
          )
        )
      )
    }, server = FALSE)
  })
  
  output$admin_status <- reactive({
    admin_status()
  })
  outputOptions(output, 'admin_status', suspendWhenHidden = FALSE)
}

# Run the app
shinyApp(ui = ui, server = server)