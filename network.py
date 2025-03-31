# Standard libraries
import random
import logging
import copy

# Third-party libraries
import networkx as nx

# Project modules
from node import Node

class Network:
    """Represents the financial network containing nodes and their debt relationships."""
    def __init__(self, mini, maxi):
        self.mini = mini
        self.maxi = maxi
        self.nodes = []
        self.graph = nx.DiGraph()
        self.original_graph = None
        self.init_network()

    def init_network(self):
        """Creates nodes and edges for a new network."""
        self.size = random.randint(self.mini, self.maxi)
        self.graph = nx.DiGraph()
        self.nodes = []

        # Step 1: Create node data placeholders
        temp_nodes_data = []
        for i in range(self.size):
            equity = random.randint(50, 1000)
            temp_nodes_data.append({'id': i, 'equity': equity, 'debts': {}})
            self.graph.add_node(i, equity=equity)

        # Step 2: Create Node objects and assign initial debts
        extra_debts_count = [max(0, int(self.size * random.uniform(0.1, 0.5)) - 1) for _ in range(self.size)]

        for i in range(self.size):
            current_id = i
            debts = {}

            if self.size > 1:
                debtor_id, debt_value = self.create_debt_link(current_id, debts)
                # Check if link creation was successful (found unique debtor)
                if debtor_id is not None:
                    debts[debtor_id] = debt_value
                    self.graph.add_edge(current_id, debtor_id, debt=debt_value)

            for _ in range(extra_debts_count[i]):
                 if len(debts) < self.size - 1:
                    debtor_id, debt_value = self.create_debt_link(current_id, debts)
                    if debtor_id is not None:
                        debts[debtor_id] = debt_value
                        self.graph.add_edge(current_id, debtor_id, debt=debt_value)

            node = Node(current_id, temp_nodes_data[i]['equity'], debts)
            self.nodes.append(node)

        # Step 3: Add potential reciprocal debts
        edges_to_consider = list(self.graph.edges())
        for u, v in edges_to_consider:
             if random.random() < 0.3 and not self.graph.has_edge(v, u):
                reciprocal_debt_value = random.randint(50, 1000)
                node_v = self.get_node_by_id(v)
                if node_v:
                    self.graph.add_edge(v, u, debt=reciprocal_debt_value)
                    node_v.debts[u] = reciprocal_debt_value
                    logging.debug(f"Added reciprocal debt from {v} to {u}: {reciprocal_debt_value}")
                else:
                     logging.warning(f"Could not find node {v} to add reciprocal debt.")

        # Final Step: Save the initial state for reset
        self.original_graph = self.graph.copy()
        logging.info(f"Initialized network with {self.size} nodes.")

    def get_node_by_id(self, node_id):
        """Helper to find a node object by its ID."""
        if 0 <= node_id < len(self.nodes):
            # Assumes node IDs match list index
            return self.nodes[node_id]
        return None

    def create_debt_link(self, current_id, existing_debts):
        """Helper to find a unique debtor and assign a debt value."""
        debtor_id = self.get_unique_debtor(current_id, existing_debts, self.size)
        if debtor_id is None:
            return None, None
        debt_value = random.randint(50, 1000)
        return debtor_id, debt_value

    def total_network_equity(self):
        """Calculates the sum of equities of all nodes."""
        return sum(node.equity for node in self.nodes)

    def total_network_debt(self):
        """Calculates the sum of total debts owed by all nodes."""
        return sum(node.total_debt() for node in self.nodes)

    def get_unique_debtor(self, current_id, debts, size):
        """Finds a node ID (debtor) that `current_id` does not already owe money to."""
        possible_debtors = [idx for idx in range(size) if idx != current_id and idx not in debts]
        if not possible_debtors:
            logging.warning(f"Node {current_id} cannot find a unique debtor among {size} nodes.")
            return None
        debtor_id = random.choice(possible_debtors)
        return debtor_id

    def defaulted_nodes_count(self):
        """Counts the number of nodes currently marked as defaulted."""
        return sum(1 for node in self.nodes if node.defaulted)

    def reset(self):
        """Resets all nodes to their initial state and reconstructs the graph structure."""
        logging.info("Resetting network to initial state...")
        
        # Step 1: Reset all nodes to their initial state
        for node in self.nodes:
            node.reset()
        
        # Step 2: Rebuild the graph from the reset nodes' debts
        self.graph = nx.DiGraph()
        
        # First add all nodes
        for node in self.nodes:
            self.graph.add_node(node.id, equity=node.equity)
        
        # Then add all edges based on node debts
        for node in self.nodes:
            for creditor_id, debt_value in node.debts.items():
                if debt_value > 1e-9:  # Only add edges for significant debts
                    self.graph.add_edge(node.id, creditor_id, debt=debt_value)
        
        logging.info("Network has been reset to its initial state.")
        return True

    def survived_nodes_count(self):
        """Counts the number of nodes currently not marked as defaulted."""
        return sum(1 for node in self.nodes if not node.defaulted)