import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os
from network import Network
from networkgraph import NetworkGraph

# Comment these if program freezes due to extensive results
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

if __name__ == '__main__':
    logging.basicConfig(filename='default.log', level=logging.INFO)
    network = Network(5, 20)
    app = NetworkGraph(network)
    app.mainloop()
