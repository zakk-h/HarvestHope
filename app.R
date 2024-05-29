library(shiny)
library(tidyverse)
library(plotly)
library(DT)

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
    TRUE ~ Section
  ))

inventory_summary_combined <- inventory_combined %>%
  group_by(Combined_Section) %>%
  summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))

colors <- c("deepskyblue", "mediumpurple", "plum", "forestgreen", "orange", "orchid", "gold", "lightcoral", "blueviolet", "darkorchid")

ui <- fluidPage(
  titlePanel("Inventory Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sections", "Select Sections:", 
                         choices = unique(inventory_combined$Combined_Section), 
                         selected = unique(inventory_combined$Combined_Section)),
      hr(),
      helpText("Data visualization and interactive table for inventory management.")
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      DTOutput("dataTable")
    )
  )
)

server <- function(input, output) {
  filtered_data <- reactive({
    inventory_combined %>%
      filter(Combined_Section %in% input$sections)
  })
  
  output$barPlot <- renderPlotly({
    data <- filtered_data() %>%
      group_by(Combined_Section) %>%
      summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
    
    plot_ly(data, x = ~reorder(Combined_Section, -Total_Quantity), y = ~Total_Quantity, type = 'bar', color = ~Combined_Section, colors = colors) %>%
      layout(title = 'Total Quantity of Items by Combined Section',
             xaxis = list(title = 'Combined Section'),
             yaxis = list(title = 'Total Quantity'))
  })
  
  output$dataTable <- renderDT({
    datatable(filtered_data(), options = list(pageLength = 10, autoWidth = TRUE))
  })
}

shinyApp(ui = ui, server = server)
