# Standard libraries
import logging
import copy
import os

# Third-party libraries
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox # Explicit import for messagebox

# Project modules
from network import Network
from eisenbergnoe import EisenbergNoe
from compression import Compression
# Simulation is imported locally


class NetworkGraph(tk.Tk):
    """Main application window displaying the network and controls."""
    def __init__(self, network, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Financial Network Simulation")
        self.network = network # The current Network instance
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- Labels ---
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.net_eq_label = tk.Label(self.info_frame)
        self.net_debt_label = tk.Label(self.info_frame)
        self.defaulted_nodes_label = tk.Label(self.info_frame)
        self.survived_nodes_label = tk.Label(self.info_frame)
        self.pareto_improvement_label = tk.Label(self.info_frame, text="Pareto Improvement: -")

        self.net_eq_label.pack(side=tk.LEFT, padx=10)
        self.net_debt_label.pack(side=tk.LEFT, padx=10)
        self.defaulted_nodes_label.pack(side=tk.LEFT, padx=10)
        self.survived_nodes_label.pack(side=tk.LEFT, padx=10)
        self.pareto_improvement_label.pack(side=tk.LEFT, padx=10)

        self.last_pareto_status = None

        # --- Buttons ---
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.en_button = tk.Button(self.button_frame, text="EisenbergNoe",
                                   command=self.eisenberg_noe_apply)
        self.comp_button = tk.Button(self.button_frame, text="Compression",
                                     command=self.compression_apply)
        self.reset_button = tk.Button(self.button_frame, text="Reset",
                                      command=self.reset)
        self.new_graph_button = tk.Button(self.button_frame, text="New Graph",
                                          command=self.new_graph)
        self.simulation_button = tk.Button(self.button_frame,
                                           text="Run Simulation",
                                           command=self.run_simulation)
        self.quit_button = tk.Button(self.button_frame, text="Quit",
                                     command=self.quit_command)

        # Pack buttons
        self.en_button.pack(side=tk.LEFT, padx=5)
        self.comp_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.new_graph_button.pack(side=tk.LEFT, padx=5)
        self.simulation_button.pack(side=tk.LEFT, padx=5)
        self.quit_button.pack(side=tk.RIGHT, padx=5) # Quit on the right

        # --- Initial Network Drawing ---
        self.pos = nx.spring_layout(self.network.graph, seed=42)
        self.pos = dict(sorted(self.pos.items()))
        self.update_labels()
        self.draw_network()

    def run_simulation(self):
        """Runs the simulation comparing EN vs Compression+EN."""
        from simulation import Simulation # Import locally
        logging.info("Starting simulation...")
        try:
            sim = Simulation(self)
            sim.run()
            logging.info("Simulation finished.")
            messagebox.showinfo("Simulation Complete", "Simulation finished. Check console and summary_results.xlsx for results.")
        except Exception as e:
            logging.exception("Error during simulation run:")
            messagebox.showerror("Simulation Error", f"An error occurred during simulation: {e}")


    def update_labels(self):
        """Updates the text of the information labels."""
        self.net_eq_label.config(text=f"Total Equity: {self.network.total_network_equity():.2f}")
        self.net_debt_label.config(text=f"Total Debt: {self.network.total_network_debt():.2f}")
        self.defaulted_nodes_label.config(text=f"Defaulted Nodes: {self.network.defaulted_nodes_count()}")
        self.survived_nodes_label.config(text=f"Survived Nodes: {self.network.survived_nodes_count()}")
        pareto_text = "-" if self.last_pareto_status is None else ("Yes" if self.last_pareto_status else "No")
        self.pareto_improvement_label.config(text=f"Pareto Improvement: {pareto_text}")

    def quit_command(self):
        """Logs and quits the application."""
        logging.info("Quit button pressed. Exiting application.")
        self.quit()
        self.destroy() # Ensure the window closes properly

    def draw_network(self):
        """Clears the figure and redraws the current network state."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        colors = {node.id: node.colour for node in self.network.nodes}
        node_colors = [colors.get(node_id, 'gray') for node_id in self.network.graph.nodes()]

        labels = {
            node.id: f'ID: {node.id}\nEquity: {node.equity:.2f}\nDebt: {node.total_debt():.2f}\nDefaulted: {node.defaulted}'
            for node in self.network.nodes}
        current_nodes = list(self.network.graph.nodes())
        if set(self.pos.keys()) != set(current_nodes):
             logging.warning("Position map doesn't match current graph nodes. Recalculating layout.")
             self.pos = nx.spring_layout(self.network.graph, seed=42)
             self.pos = dict(sorted(self.pos.items()))

        nx.draw(self.network.graph, pos=self.pos, with_labels=False,
                node_color=node_colors, node_size=1200, alpha=0.9,
                ax=ax)
        nx.draw_networkx_labels(self.network.graph, pos=self.pos, labels=labels, font_size=8, ax=ax)
        nx.draw_networkx_edges(self.network.graph, pos=self.pos, ax=ax, arrowstyle='->', arrowsize=15, edge_color='gray', alpha=0.6)

        ax.set_title("Financial Network")
        self.canvas.draw()

    def eisenberg_noe_apply(self):
        """Applies the Eisenberg-Noe algorithm to the current network."""
        logging.info("Applying EisenbergNoe algorithm...")
        eisenberg_noe = EisenbergNoe(self.network)
        eisenberg_noe.apply()
        logging.info("EisenbergNoe algorithm applied.")

        self.last_pareto_status = eisenberg_noe.is_pareto_improvement()
        self.update_labels()
        self.draw_network()

    def compression_apply(self):
        """Applies the debt compression algorithm."""
        logging.info("Applying Compression algorithm...")
        Compression(self.network).apply()
        logging.info("Compression algorithm applied.")
        self.last_pareto_status = None
        self.update_labels()
        self.draw_network()

    def reset(self):
        """Resets the network to its initial state when it was first loaded/generated."""
        logging.info("Resetting network to initial state...")
        self.network.reset()
        self.last_pareto_status = None
        self.pos = nx.spring_layout(self.network.graph, seed=42)
        self.pos = dict(sorted(self.pos.items()))
        self.update_labels()
        self.draw_network()
        logging.info("Network reset.")

    def new_graph(self):
        """Generates and displays a completely new network."""
        logging.info("Generating new graph...")
        self.network = Network(5, 20)

        self.pos = nx.spring_layout(self.network.graph, seed=42)
        self.pos = dict(sorted(self.pos.items()))

        self.last_pareto_status = None
        self.update_labels()
        self.draw_network()
        logging.info("New graph generated.")
