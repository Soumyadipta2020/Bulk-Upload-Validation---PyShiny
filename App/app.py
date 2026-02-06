from shiny import App

# Import the segregated UI and server modules
from App.ui import app_ui
from App.server import server


# App instantiation
app = App(app_ui, server)
