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
    TRUE ~ Section #Else, we label them as they already were
  ))

inventory_summary_combined <- inventory_combined %>%
  group_by(Combined_Section) %>%
  summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))


colors <- c("deepskyblue", "mediumpurple", "plum", "forestgreen", "orange", "orchid", "gold", "lightcoral", "blueviolet", "darkorchid")

#Default state of the UI
ui <- fluidPage( #Responsive
  titlePanel("Inventory Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("sections", "Select Sections:", 
                         choices = unique(inventory_combined$Combined_Section), 
                         selected = unique(inventory_combined$Combined_Section)), #All initially
      hr(), #Horizontal Line for visual separation
      helpText("Data visualization and interactive table for inventory management.")
    ),
    mainPanel(
      plotlyOutput("barPlot"),
      DTOutput("dataTable")
    )
  )
)
#Server function - handles reactive logic and rendering outputs based on inputs
#The input object contains all the inputs from the UI
#The output object is used to send reactive output to the UI
#Each time there is a change in the input, Shiny does not re-run the whole server function. 
#It only re-evaluates the reactive expressions and render functions that depend on the changed input. 
server <- function(input, output) {
  filtered_data <- reactive({ #any change in the user input (the selected sections) triggers a re-evaluation of the filtered data.
    inventory_combined %>%
      filter(Combined_Section %in% input$sections) #only contains sections selected by the user
  })
  #renderPlotly takes an expression (enclosed in {}) that generates the Plotly plot.
  #This expression is evaluated in a reactive context, meaning that Shiny will automatically re-run this expression whenever any reactive dependencies change.
  #This is essentially the expr parameter. It wants an enclosed code chunk to execute.
  output$barPlot <- renderPlotly({ #renderPlotly wraps plot_ly, renders reactively
    data <- filtered_data() %>% #Defined using reactive, so it is a function
      group_by(Combined_Section) %>%
      summarise(Total_Quantity = sum(Quantity, na.rm = TRUE))
    
    plot_ly(data, x = ~reorder(Combined_Section, -Total_Quantity), y = ~Total_Quantity, type = 'bar', color = ~Combined_Section, colors = colors) %>%
      layout(title = 'Total Quantity of Items by Combined Section',
             xaxis = list(title = 'Combined Section'),
             yaxis = list(title = 'Total Quantity'))
  })
  
  #Render datatable reactively
  #filtered_data is a reactive expression.
  #To access the filtered data, call filtered_data(), which triggers the evaluation of the reactive expression and returns the filtered dataset.
  #It doesn't evaluate until it needs it. It will check if the upstream, input$sections has changed. If it has, it will recompute. Otherwise, use cache.
  output$dataTable <- renderDT({
    datatable(filtered_data(), options = list(pageLength = 10, autoWidth = TRUE))
  })
}

#Runs the app
shinyApp(ui = ui, server = server)
