from network import Network
import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os

class EisenbergNoe:
    def __init__(self, network):  # Constructor method to initialize the EisenbergNoe class
        self.network = network  # Network instance to apply Eisenberg Noe
        self.initial_equities = {node.id: node.equity for node in network.nodes}  # Dictionary storing initial equities of nodes

    def apply(self):  # Method to apply the Eisenberg Noe model
        debts_cleared = True
        while debts_cleared:  # Iterate until no debts are cleared
            debts_cleared = False  # Set debts_cleared to False at the start of each iteration
            for node in sorted(self.network.nodes, key=lambda x: x.id):  # Iterate over sorted nodes
                original_debts = dict(node.debts)  # Keep a copy of the original debts
                self.clear_debts(node)  # Call to method to clear the debts
                if node.debts != original_debts:  # If the debts have changed, set debts_cleared to True
                    debts_cleared = True

        for node in self.network.nodes:  # After all iterations, set the defaulted value of each node based on its final equity value
            node.equity = round(node.equity, 2)  # Round equity to 2 decimal places
            node.defaulted = node._equity < node.total_debt()  # Node is defaulted if equity is less than total debt
            print(f"{node.id} is: Defaulted: {node.defaulted}")  # Print the defaulted status of node

    def is_pareto_improvement(self):  # Method to check for Pareto improvement
        for node in self.network.nodes:  # For each node in the network
            if node.equity < self.initial_equities[node.id]:  # If node's equity is less than the initial equity
                return False  # Return False indicating no Pareto improvement
        return True  # If all nodes' equities are greater or equal to initial equities, return True indicating Pareto improvement

    def clear_debts(self, node):  # Method to clear the debts of a node
        total_debt = node.total_debt()  # Total debt of the node
        if total_debt == 0:  # If total debt is zero, no need to clear, so return
            return
        debt_items = list(node.debts.items())  # List of debtor ID and debt pairs
        for debtor_id, owed in debt_items:  # For each debtor ID and debt pair
            debtor = self.network.nodes[debtor_id]  # Get the debtor node
            payment = (owed / total_debt) * node.equity  # Calculate payment
            node.equity -= payment  # Deduct payment from node's equity
            debtor.equity += payment  # Add payment to debtor's equity
            if debtor_id in node.debts:  # If debtor ID exists in node's debts
                node.debts[debtor_id] -= payment  # Deduct payment from the debt owed
                if node.debts[debtor_id] <= 0:  # If the debt owed is now zero or less
                    del node.debts[debtor_id]  # Delete the debt entry
                    if self.network.graph.has_edge(node.id, debtor_id):  # If an edge exists from node to debtor in the graph
                        self.network.graph.remove_edge(node.id, debtor_id)  # Remove the edge
                    logging.info(f"Node {node.id} paid off all its debts.")  # Log that node has paid off all its debts
            node.update_color()  # Update node's color
            debtor.update_color()  # Update debtor's color
            node.defaulted = node.equity < node.total_debt()  # Set node's defaulted status based on its equity and total debt
            debtor.defaulted = debtor.equity < debtor.total_debt()  # Set debtor's defaulted status based on its equity and total debt

    def node_equity_change(self):  # Method to calculate and print equity change for each node
        for node in self.network.nodes:  # For each node in the network
            print(f'Node {node.id} Equity Change: {node.equity - self.initial_equities[node.id]}')  # Print the equity change of the node
