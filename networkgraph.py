from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from network import Network
# from simulation import Simulation
from eisenbergnoe import EisenbergNoe
from compression import Compression
import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os

class NetworkGraph(tk.Tk):
    def __init__(self, network, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.network = network
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.net_eq_label = tk.Label(self)
        self.net_debt_label = tk.Label(self)
        self.net_eq_label.pack()
        self.net_debt_label.pack()
        self.defaulted_nodes_label = tk.Label(self)
        self.defaulted_nodes_label.pack()
        self.survived_nodes_label = tk.Label(self)
        self.survived_nodes_label.pack()
        self.pareto_improvement_label = tk.Label(self, text="Pareto Improvement: -")
        self.pareto_improvement_label.pack()
        self.update_labels()

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.en_button = tk.Button(self.button_frame, text="EisenbergNoe",
                                   command=self.eisenberg_noe_apply)
        self.en_button.pack(side=tk.LEFT)

        self.comp_button = tk.Button(self.button_frame, text="Compression",
                                     command=self.compression_apply)
        self.comp_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.button_frame, text="Quit",
                                     command=self.quit_command)
        self.quit_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.button_frame, text="Reset",
                                      command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        self.new_graph_button = tk.Button(self.button_frame, text="NewGraph",
                                          command=self.new_graph)
        self.new_graph_button.pack(side=tk.LEFT)

        self.simulation_button = tk.Button(self.button_frame,
                                           text="Run Simulation",
                                           command=self.run_simulation)
        self.simulation_button.pack(side=tk.LEFT)

        self.pos = nx.spring_layout(self.network.graph)
        self.pos = dict(sorted(self.pos.items()))
        self.draw_network()

    def run_simulation(self):
        from simulation import Simulation
        sim = Simulation(self)
        sim.run()

    def update_labels(self):
        self.net_eq_label.config(text=f"Total Equity: {self.network.total_network_equity()}")
        self.net_debt_label.config(text=f"Total Debt: {self.network.total_network_debt()}")
        self.defaulted_nodes_label.config(text=f"Defaulted Nodes: {self.network.defaulted_nodes_count()}")
        self.survived_nodes_label.config(text=f"Survived Nodes: {self.network.survived_nodes_count()}")
        self.pareto_improvement_label.config(text=f"Pareto Improvement: -")

    def quit_command(self):
        logging.info("Quit button pressed.")
        self.quit()

    def draw_network(self):
        self.fig.clear()
        colors = {node.id: node.colour for node in self.network.nodes}
        labels = {
            node.id: f'ID: {node.id}\nEquity: {node.equity:.2f}\nDebt: {node.total_debt():.2f}\nDefaulted: {node.defaulted}'
            for node in self.network.nodes}
        nx.draw(self.network.graph, pos=self.pos, with_labels=True, labels=labels,
                node_color=[colors[node] for node in self.network.graph.nodes()],
                ax=self.fig.add_subplot(111))
        self.update_labels()
        self.canvas.draw()


    def eisenberg_noe_apply(self):
        eisenberg_noe = EisenbergNoe(self.network)
        eisenberg_noe.apply()
        eisenberg_noe.node_equity_change()  # Print the equity changes for each node
        self.draw_network()
        logging.info("EisenbergNoe algorithm applied.")
        self.update_labels()

        # Update Pareto Improvement status
        pareto_improvement_status = "Yes" if eisenberg_noe.is_pareto_improvement() else "No"
        self.pareto_improvement_label.config(text=f"Pareto Improvement: {pareto_improvement_status}")

    def compression_apply(self):
        Compression(self.network).apply()
        self.draw_network()
        logging.getLogger('default.log').info("Compression algorithm applied.")
        self.update_labels()

    def reset(self):
        self.network.reset()
        self.draw_network()
        self.update_labels()
        self.pareto_improvement_label.config(text=f"Pareto Improvement: -")

    def new_graph(self):
        # Generate a new network (e.g., with the same number of nodes and edges as before for simplicity)
        self.network = Network(5, 10)  # Adjust these values if needed

        # Update the graph layout
        self.pos = nx.spring_layout(self.network.graph)
        self.pos = dict(sorted(self.pos.items()))

        # Update all labels
        self.update_labels()

        # Draw the updated network
        self.draw_network()

        logging.info("New graph generated.")