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


class Compression:
    def __init__(self, network):  # Initialize the Compression class with the network instance
        self.network = network

    def apply(self):  # Apply the compression algorithm to the network
        for node in self.network.nodes:  # Loop through each node in the network
            self.calculate_net_debt(node)  # Calculate the net debt of the node
            self.simplify_debts(node)  # Simplify the debts of the node
            node.defaulted = node.equity < node.total_debt()  # Update defaulted status of the node based on its equity and total debt
            node.colour = 'red' if node.defaulted is True else 'green'  # Update the color of the node based on its defaulted status

    def calculate_net_debt(self, node):  # Method to calculate net debt between each pair of nodes
        debt_items = list(node.debts.items())  # Get a list of debtor id and owed amount pairs
        for debtor_id, owed in debt_items:  # For each debtor id and owed amount pair
            if debtor_id in node.debts and node.id in self.network.nodes[debtor_id].debts:  # Check if there is mutual debt between the nodes
                reciprocal_debt = self.network.nodes[debtor_id].debts[node.id]  # Get the reciprocal debt owed by the debtor to the node
                net_debt = owed - reciprocal_debt  # Calculate the net debt between the two nodes
                print(f"Net debt between node {node.id} and node {debtor_id} is: {net_debt}")  # Print the net debt

    def simplify_debts(self, node):  # Method to simplify debts between each pair of nodes
        debt_items = list(node.debts.items())  # Get a list of debtor id and owed amount pairs
        for debtor_id, owed in debt_items:  # For each debtor id and owed amount pair
            if debtor_id in node.debts and node.id in self.network.nodes[debtor_id].debts:  # Check if there is mutual debt between the nodes
                reciprocal_debt = self.network.nodes[debtor_id].debts[node.id]  # Get the reciprocal debt owed by the debtor to the node
                if owed <= reciprocal_debt:  # If owed amount is less than or equal to the reciprocal debt
                    self.network.nodes[debtor_id].debts[node.id] -= owed  # Subtract owed amount from the debtor's debt
                    del node.debts[debtor_id]  # Delete the debt entry from the node's debts
                    if self.network.graph.has_edge(node.id, debtor_id):  # If an edge exists between the nodes in the graph
                        self.network.graph.remove_edge(node.id, debtor_id)  # Remove the edge
                else:  # If owed amount is more than the reciprocal debt
                    node.debts[debtor_id] -= reciprocal_debt  # Subtract reciprocal debt from the node's owed amount
                    del self.network.nodes[debtor_id].debts[node.id]  # Delete the reciprocal debt entry from the debtor's debts
                    if self.network.graph.has_edge(debtor_id, node.id):  # If an edge exists between the nodes in the graph
                        self.network.graph.remove_edge(debtor_id, node.id)  # Remove the edge
            node.defaulted = node.equity < node.total_debt()  # Update defaulted status of the node based on its equity and total debt
            node.colour = 'red' if node.defaulted is True else 'green'  # Update the color of the node based on its defaulted status
            debtor = self.network.nodes[debtor_id]  # Get the debtor node
            debtor.defaulted = debtor.equity < debtor.total_debt()  # Update defaulted status of the debtor based on its equity and total debt
            debtor.colour = 'red' if debtor.defaulted is True else 'green'  # Update the color of the debtor based on its defaulted status

