
import app


# Set the server binding address and port
bind = "0.0.0.0:5001"
# Set the number of workers based on the CPU count
workers = 4
# Define the server hook for the 'on_starting' event
on_starting = app.on_starting
# Set the timeout to 2 mins
timeout = 300