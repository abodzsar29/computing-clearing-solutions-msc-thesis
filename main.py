# Standard libraries
import logging
import os # Keep if needed elsewhere
import tkinter as tk

# Third-party libraries
import pandas as pd

# Project modules
from network import Network
from networkgraph import NetworkGraph

# Configure pandas display options
try:
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 50)
except Exception as e:
    logging.warning(f"Could not set pandas display options: {e}")

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(filename='default.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Application starting...")

    try:
        # Create the network model
        network = Network(mini=5, maxi=15)

        # Create the GUI application window
        app = NetworkGraph(network)

        # Start the Tkinter event loop
        app.mainloop()

        logging.info("Application finished normally.")

    except Exception as e:
        logging.exception("An error occurred during application execution:")
        # Fallback error reporting if GUI fails early
        print(f"FATAL ERROR: {e}")