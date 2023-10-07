import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os
from node import Node

class Network:
    def __init__(self, mini, maxi):  # Constructor method to initialize the Network class
        self.mini = mini  # Minimum network size
        self.maxi = maxi  # Maximum network size
        self.init_network()  # Initialization of the network

    def init_network(self):  # Method to initialize the network
        self.size = random.randint(self.mini, self.maxi)  # Determine the network size randomly between mini and maxi
        self.graph = nx.DiGraph()  # Initialize a directed graph for the network
        more_debts_size = [int(self.size * random.uniform(0.1, 1)) - 1 for _ in range(self.size)]  # Precompute sizes for debts
        self.nodes = [self.create_node(i, more_debts_size) for i in range(self.size)]  # Create nodes in the network
        for node in self.nodes:  # Ensure at least one creditor for each node
            if node.total_debt() == 0:  # If a node has no debts
                creditor_node = self.get_unique_creditor(node, self.nodes)  # Get a unique creditor for the node
                debt_value = random.randint(50, 1000)  # Assign a random debt value
                node.debts[creditor_node.id] = debt_value  # Add debt to the node
                self.graph.add_edge(node.id, creditor_node.id, debt=debt_value)  # Add an edge in the graph for the debt
        self.original_graph = self.graph.copy()  # Save a copy of the original graph

    def create_node(self, current_id, more_debts_size):  # Method to create a node
        debts = {}  # Initialize debts dictionary
        debtor_id, debt_value = self.create_debt(current_id, debts)  # Ensure at least one debt for the node
        self.graph.add_edge(current_id, debtor_id, debt=debt_value)  # Add an edge in the graph for the debt
        debts_data = [(self.create_debt(current_id, debts)) for _ in range(more_debts_size[current_id])]  # Create more debts
        for debtor_id, debt_value in debts_data:  # For each debtor and debt value pair
            self.graph.add_edge(current_id, debtor_id, debt=debt_value)  # Add an edge for the debt
            if random.random() < 0.5:  # With a 50% chance
                self.graph.add_edge(debtor_id, current_id, debt=debt_value)  # Add an edge for the debt in reverse direction
        # equity = (sum(debts.values())) * round(random.uniform(0.5, 1.5), 2)  # Calculate equity as a sum of debts times a random factor
        equity = random.randint(50, 1000)  # Assign a random equity value
        self.graph.add_node(current_id, equity=equity)  # Add the node to the graph with the calculated equity
        return Node(current_id, equity, debts)  # Return the created Node

    def create_debt(self, current_id, debts):  # Method to create a debt
        debtor_id = self.get_unique_debtor(current_id, debts, self.size)  # Get a unique debtor ID
        debt_value = random.randint(50, 1000)  # Assign a random debt value
        debts[debtor_id] = debt_value  # Add debt to the debts dictionary
        return debtor_id, debt_value  # Return the debtor ID and debt value

    def total_network_equity(self):  # Method to calculate total network equity
        return sum(node.equity for node in self.nodes)  # Return the sum of equities for all nodes

    def total_network_debt(self):  # Method to calculate total network debt
        return sum(node.total_debt() for node in self.nodes)  # Return the sum of total debts for all nodes

    def get_unique_debtor(self, current_id, debts, size):  # Method to get a unique debtor ID
        debtor_id = random.choice([idx for idx in range(size) if idx != current_id])  # Choose a debtor ID not equal to current ID
        while debtor_id in debts:  # If the chosen debtor ID is already in debts
            debtor_id = random.choice([idx for idx in range(size) if idx != current_id])  # Choose another debtor ID
        return debtor_id  # Return the debtor ID

    def get_unique_creditor(self, current_node, nodes): # Method to get a unique creditor
        creditor_node = random.choice([other_node for other_node in nodes if other_node != current_node])  # Choose a creditor not equal to current node
        while creditor_node.id in current_node.debts:  # If the chosen creditor is already in the current node's debts
            creditor_node = random.choice([other_node for other_node in nodes if other_node != current_node])  # Choose another creditor
        return creditor_node  # Return the creditor node

    def defaulted_nodes_count(self):  # Method to count defaulted nodes
        return sum(1 for node in self.nodes if node.defaulted)  # Return the sum of defaulted nodes

    def reset(self):  # Method to reset the network
        for node in self.nodes:  # For each node in the network
            node.reset()  # Reset the node
        self.graph = self.original_graph.copy()  # Reset the graph to its original state
        logging.info("Network has been reset.")  # Log the reset action

    def survived_nodes_count(self):  # Method to count survived nodes
        return sum(1 for node in self.nodes if not node.defaulted)  # Return the sum of survived nodes
