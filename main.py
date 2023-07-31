import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy


class Node:
    # Constructor of the class, called when an object of the class is initialized.
    def __init__(self, id, equity, debts):
        self.id = id  # Assigns the provided id to the instance
        self._equity = equity  # Assigns the provided equity to the private instance variable _equity
        self.initial_equity = equity  # Stores the initial equity value for potential later use
        self._debts = debts  # Assigns the provided debts to the private instance variable _debts
        self.initial_debts = copy.deepcopy(debts)  # Stores a deep copy of the initial debts dictionary for potential later use
        self.defaulted = self.equity < self.total_debt()  # Calculates if the node has defaulted, i.e., if debts exceed equity
        self.colour = 'red' if self.defaulted is True else 'green'  # Node's color is set to red if it has defaulted, otherwise to green
        self.totaldebt = self.total_debt()  # Calculates the total debt of the node
        self.update_color()  # Calls the update_color method to set the color based on the node's financial status

    # Creates a getter for the private variable _equity
    @property
    def equity(self):
        return self._equity  # Returns the value of private variable _equity

    # Creates a setter for the private variable _equity
    @equity.setter
    def equity(self, value):
        self._equity = value  # Sets the value of private variable _equity
        self.update_color()  # Calls the update_color method after the equity is changed

    # Creates a getter for the private variable _debts
    @property
    def debts(self):
        return self._debts  # Returns the value of private variable _debts.

    # Creates a setter for the private variable _debts
    @debts.setter
    def debts(self, value):
        self._debts = value  # Sets the value of private variable _debts
        self.update_color()  # Calls the update_color method after the debts are changed

    # Calculates and returns the total debt
    def total_debt(self):
        return sum(self.debts.values())  # Returns the sum of all debts

    # Resets the node's equity and debts to their initial values and updates the color
    def reset(self):
        self.equity = self.initial_equity  # Resets the equity to its initial value
        self.debts = copy.deepcopy(self.initial_debts)  # Resets the debts to their initial values
        self.update_color()  # Calls the update_color method after the reset

    # Checks the defaulted state and updates the color accordinly
    def update_color(self):
        self.defaulted = self._equity < self.total_debt()  # Checks if the node has defaulted after changes to equity or debts
        self.colour = 'red' if self.defaulted else 'green'  # Sets the color to red if the node has defaulted, otherwise to green


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
        equity = sum(debts.values()) * round(random.uniform(0.1, 0.5), 2)  # Calculate equity as a sum of debts times a random factor
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

    def get_unique_creditor(self, current_node, nodes):  # Method to get a unique creditor
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

        self.en_button = tk.Button(self, text="EisenbergNoe", command=self.eisenberg_noe_apply)
        self.en_button.pack()

        self.comp_button = tk.Button(self, text="Compression", command=self.compression_apply)
        self.comp_button.pack()

        self.quit_button = tk.Button(self, text="Quit", command=self.quit_command)
        self.quit_button.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset)
        self.reset_button.pack()

        self.pos = nx.spring_layout(self.network.graph)
        self.pos = dict(sorted(self.pos.items()))
        self.draw_network()

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


if __name__ == '__main__':
    logging.basicConfig(filename='default.log', level=logging.INFO)
    network = Network(5, 10)
    app = NetworkGraph(network)
    app.mainloop()
