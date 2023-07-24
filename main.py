import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy


class Node:
    def __init__(self, id, equity, debts):
        self.id = id
        self.equity = equity
        self.initial_equity = equity
        self.debts = debts
        self.initial_debts = copy.deepcopy(debts)
        self.defaulted = False

    def total_debt(self):
        return sum(self.debts.values())

    def reset(self):
        self.equity = self.initial_equity
        self.debts = copy.deepcopy(self.initial_debts)
        self.defaulted = self.equity < self.total_debt()


class Network:
    def __init__(self, mini, maxi):
        self.mini = mini
        self.maxi = maxi
        self.init_network()

    def init_network(self):
        self.size = random.randint(self.mini, self.maxi)
        self.nodes = []
        self.graph = nx.DiGraph()
        for i in range(self.size):
            debts = {}
            for _ in range(int(self.size * random.uniform(0.1, 1))):
                debtor_id = random.choice(range(self.size))
                if debtor_id != i:
                    debt_value = random.randint(50, 1000)
                    debts[debtor_id] = debt_value
                    self.graph.add_edge(i, debtor_id, debt=debt_value)
                    if random.random() < 0.5:
                        self.graph.add_edge(debtor_id, i, debt=debt_value)
            equity = sum(debts.values()) * round(random.uniform(0.25, 1.25), 2)
            self.graph.add_node(i, equity=equity)
            node = Node(i, equity, debts)
            self.nodes.append(node)
            print(f"The equity of node {i} is: {equity}, and debt is {sum(debts.values())}")
            node.defaulted = node.equity < node.total_debt()
        # Keep a copy of the original graph for resetting later
        self.original_graph = self.graph.copy()

    def reset(self):
        for node in self.nodes:
            node.reset()
        # Reset the graph to its original state
        self.graph = self.original_graph.copy()


class EisenbergNoe:
    def __init__(self, network):
        self.network = network

    def apply(self):
        debts_cleared = True
        while debts_cleared:
            debts_cleared = False
            for node in sorted(self.network.nodes, key=lambda x: x.id):
                original_debts = dict(node.debts)
                self.clear_debts(node)
                if node.debts != original_debts:
                    debts_cleared = True

        # After all iterations have completed, set the defaulted value of each node based on its final equity value
        for node in self.network.nodes:
            node.defaulted = node.equity <= 0
            if node.defaulted:
                logging.info(f'Node {node.id} defaulted.')
            else:
                logging.info(f'Node {node.id} has positive equity.')

    def clear_debts(self, node):
        total_debt = node.total_debt()
        if total_debt == 0:
            return
        debt_items = list(node.debts.items())
        for debtor_id, owed in debt_items:
            debtor = self.network.nodes[debtor_id]
            payment = (owed / total_debt) * node.equity
            node.equity -= payment
            debtor.equity += payment
            if debtor_id in node.debts:
                node.debts[debtor_id] -= payment
                if node.debts[debtor_id] <= 0:
                    del node.debts[debtor_id]



class Compression:
    def __init__(self, network):
        self.network = network

    def apply(self):
        for node in self.network.nodes:
            self.simplify_debts(node)

    def simplify_debts(self, node):
        debt_items = list(node.debts.items())  # create a copy of items
        for debtor_id, owed in debt_items:
            if debtor_id in node.debts and node.id in self.network.nodes[debtor_id].debts:
                reciprocal_debt = self.network.nodes[debtor_id].debts[node.id]
                if owed <= reciprocal_debt:
                    self.network.nodes[debtor_id].debts[node.id] -= owed
                    del node.debts[debtor_id]
                    if self.network.graph.has_edge(node.id, debtor_id):
                        self.network.graph.remove_edge(node.id, debtor_id)
                else:
                    node.debts[debtor_id] -= reciprocal_debt
                    del self.network.nodes[debtor_id].debts[node.id]
                    if self.network.graph.has_edge(debtor_id, node.id):
                        self.network.graph.remove_edge(debtor_id, node.id)


class NetworkGraph(tk.Tk):
    def __init__(self, network, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.network = network
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.en_button = tk.Button(self, text="EisenbergNoe", command=self.eisenberg_noe_apply)
        self.en_button.pack()

        self.comp_button = tk.Button(self, text="Compression", command=self.compression_apply)
        self.comp_button.pack()

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack()

        self.reset_button = tk.Button(self, text="Reset", command=self.reset)
        self.reset_button.pack()

        self.pos = nx.spring_layout(self.network.graph)
        self.draw_network()

    def draw_network(self):
        self.fig.clear()
        colors = ['red' if node.defaulted else 'green' for node in self.network.nodes]
        labels = {node.id: f'ID: {node.id + 1}\nEquity: {node.equity:.2f}\nDebt: {node.total_debt():.2f}' for node in self.network.nodes}
        nx.draw(self.network.graph, pos=self.pos, with_labels=True, labels=labels, node_color=colors, ax=self.fig.add_subplot(111))
        self.canvas.draw()

    def eisenberg_noe_apply(self):
        EisenbergNoe(self.network).apply()
        self.draw_network()

    def compression_apply(self):
        Compression(self.network).apply()
        self.draw_network()

    def reset(self):
        self.network.reset()
        self.draw_network()


if __name__ == '__main__':
    logging.basicConfig(filename='default.log', level=logging.INFO)
    network = Network(5, 10)
    app = NetworkGraph(network)
    app.mainloop()