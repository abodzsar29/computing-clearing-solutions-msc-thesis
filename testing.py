import unittest
import random
import copy
import tkinter as tk
from unittest.mock import Mock, patch
import networkx as nx
from node import Node
from network import Network
from eisenbergnoe import EisenbergNoe
from compression import Compression
from networkgraph import NetworkGraph


# Objective 1 - Point 1 - Checking Node Initialisation
class TestNodeInitialisation(unittest.TestCase):
    def setUp(self):
        self.node = Node(id=1,
                         equity=100,
                         debts={2: 50, 3: 25})

    # Checking whether Node ID is correctly initialised
    def test_id(self):
        self.assertEqual(self.node.id,
                         1,
                         "Node ID not initialised correctly.")

    # Checking whether Node equity is correctly initialised
    def test_equity(self):
        self.assertEqual(self.node.equity,
                         100,
                         "Node equity not initialised correctly.")
        self.assertFalse(self.node.equity < 0,
                         "Node equity cannot be negative.")
        self.assertFalse(self.node.equity is None,
                         "Node equity cannot be None.")

    # Checking whether Node debt is correctly initialised
    def test_debts(self):
        self.assertEqual(self.node.debts,
                         {2: 50, 3: 25},
                         "Node debts not initialised correctly.")
        for debt in self.node.debts.values():
            self.assertFalse(debt < 0, "Debt value cannot be negative.")
            self.assertFalse(debt is None, "Debt value cannot be None.")

    # Checking whether Node default status is correctly initialised
    def test_defaulted(self):
        self.assertEqual(self.node.defaulted,
                         False,
                         "Node defaulted status not initialised correctly.")

    # Checking whether Node colour is correctly initialised
    def test_colour(self):
        self.assertEqual(self.node.colour,
                         'green',
                         "Node colour not initialised correctly.")


# Objective 1 - Point 1 - Checking Network Initialisation
class TestNetworkInitialisation(unittest.TestCase):
    def setUp(self):
        self.network = Network(mini=5, maxi=10)

    # Checking whether network initialisation properties conform to arguments
    def test_nodes(self):
        self.assertTrue(self.network.nodes, "Network nodes not initialised.")
        self.assertTrue(5 <= len(self.network.nodes) <= 10,
                        "Network si\e not within expected range.")
        for node in self.network.nodes:
            self.assertFalse(node.equity < 0, "Node equity cannot be negative.")
            self.assertFalse(node.equity is None, "Node equity cannot be None.")
            for debt in node.debts.values():
                self.assertFalse(debt < 0, "Debt value cannot be negative.")
                self.assertFalse(debt is None, "Debt value cannot be None.")


# Objective 1 - Point 2 -
class TestEdgeDirection(unittest.TestCase):
    def setUp(self):
        random.seed(1)  # Ensuring that the random outputs are consistent
        self.network = Network(5, 10)

    def test_edge_direction(self):
        # This test will check if the direction of the links between nodes is correctly implemented.
        for node in self.network.nodes:
            for debtor_id in node.debts.keys():
                # Check if an edge exists from node.id to debtor_id. If not, the test will fail.
                self.assertTrue(self.network.graph.has_edge(node.id, debtor_id),
                                f"Expected an edge from {node.id} to {debtor_id}")

                # Check if the edge is not bidirectional unless explicitly specified. If it is, the test will fail.
                if not self.network.graph.has_edge(debtor_id, node.id):
                    self.assertFalse(self.network.graph.has_edge(debtor_id, node.id),
                                     f"Did not expect an edge from {debtor_id} to {node.id}")


# Objective 1 - Point 3
class TestEisenbergNoe(unittest.TestCase):
    def setUp(self):
        self.network = Network(5, 10)
        self.en = EisenbergNoe(self.network)

    def test_initialisation(self):
        self.assertEqual(self.en.network, self.network)
        self.assertDictEqual(self.en.initial_equities, {node.id: node.equity for node in self.network.nodes})

    def test_apply(self):
        # Save initial equity of nodes
        initial_equity = {node.id: node.equity for node in self.network.nodes}
        # Save initial debt of nodes
        initial_debts = {node.id: node.total_debt() for node in self.network.nodes}
        # Apply EisenbergNoe algorithm
        self.en.apply()
        # After apply, no node should have negative equity
        for node in self.network.nodes:
            self.assertGreaterEqual(node.equity, 0)
        # After apply, if a node still has debt, it should have zero equity
        for node in self.network.nodes:
            if node.total_debt() > 0:
                self.assertEqual(node.equity, 0)
        # After apply, if a node has equity, it should have no debt
        for node in self.network.nodes:
            if node.equity > 0:
                self.assertEqual(node.total_debt(), 0)
        # After apply, the total equity should not have increased
        final_total_equity = sum(node.equity for node in self.network.nodes)
        initial_total_equity = sum(value for value in initial_equity.values())
        self.assertLessEqual(final_total_equity, initial_total_equity)
        # After apply, the total debt should not have increased
        final_total_debt = sum(node.total_debt() for node in self.network.nodes)
        initial_total_debt = sum(value for value in initial_debts.values())
        self.assertLessEqual(final_total_debt, initial_total_debt)

    def test_pareto_improvement(self):
        self.en.apply()
        is_pareto_improvement = self.en.is_pareto_improvement()
        # If it is a pareto improvement, then no node's equity should have decreased
        if is_pareto_improvement:
            for node in self.network.nodes:
                self.assertGreaterEqual(node.equity, self.en.initial_equities[node.id])


# Objective 2
class TestObjective2(unittest.TestCase):

    def setUp(self):
        self.network = Network(5, 10)
        self.compression = Compression(self.network)
        self.app = NetworkGraph(self.network)
        self.node = self.network.nodes[0]
        self.initial_node_equity = self.node.equity
        self.initial_node_debts = self.node.debts.copy()
        self.initial_network_graph = self.network.graph.copy()

    # Objective 2 - Point 1
    def test_reset(self):
        self.network.reset()
        self.assertEqual(self.node.equity, self.initial_node_equity)
        self.assertEqual(self.node.debts, self.initial_node_debts)
        self.assertEqual(self.network.graph.edges, self.initial_network_graph.edges)

    # Verifying the copy
    def test_compression_initialisation(self):
        self.assertEqual(self.compression.network, self.network)

    # Objective 2 - Point 2
    def test_apply_compression(self):
        initial_network_graph = self.network.graph.copy()
        self.compression.apply()
        for node in self.network.nodes:
            for debtor_id, owed in list(node.debts.items()):
                self.assertNotIn(node.id, self.network.nodes[debtor_id].debts)
        self.assertNotEqual(self.network.graph.edges, initial_network_graph.edges)

    # Objective 2 - Point 2
    def test_compression_apply_in_network_graph(self):
        initial_network_graph = self.app.network.graph.copy()
        self.app.compression_apply()
        self.assertNotEqual(self.app.network.graph.edges, initial_network_graph.edges)


# Objective 3
class TestObjective3(unittest.TestCase):
    def setUp(self):
        self.network = Network(5, 5)
        self.eisenberg_noe = EisenbergNoe(self.network)

    # Objective 3 - Point 1
    def test_defaulted_nodes_count(self):
        count = self.network.defaulted_nodes_count()
        self.assertEqual(count, sum(1 for node in self.network.nodes if node.defaulted))

    # Objective 3 - Point 2
    def test_survived_nodes_count(self):

        count = self.network.survived_nodes_count()
        self.assertEqual(count, sum(1 for node in self.network.nodes if not node.defaulted))

    # Objective 3 - Point 3
    def test_is_pareto_improvement(self):
        # Apply the Eisenberg Noe algorithm before testing for Pareto improvement
        self.eisenberg_noe.apply()
        self.assertEqual(self.eisenberg_noe.is_pareto_improvement(), all(node.equity >= node.initial_equity for node in self.network.nodes))

    # Objective 3 - Point 4
    def test_total_network_equity(self):
        total_equity = self.network.total_network_equity()
        self.assertEqual(total_equity, sum(node.equity for node in self.network.nodes))

    # Objective 3 - Point 6
    def test_total_network_debt(self):
        total_debt = self.network.total_network_debt()
        self.assertEqual(total_debt, sum(node.total_debt() for node in self.network.nodes))

    # Objective 3 - Point 5
    def test_node_equity_change(self):
        # Apply the Eisenberg Noe algorithm to generate changes in equity
        self.eisenberg_noe.apply()
        for node in self.network.nodes:
            change = node.equity - node.initial_equity
            self.assertEqual(change, node.equity - self.eisenberg_noe.initial_equities[node.id])


# Testing indirect contributions of the Objectives
class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Network(5, 10)
        self.app = NetworkGraph(self.network)

    # Testing that the NetworkGraph class gets initialised correctly
    def test_networkgraph_initialisation(self):
        self.assertIsInstance(self.app, NetworkGraph)
        self.assertEqual(self.app.network, self.network)

    # Testing the correct updating of GUI labels
    def test_update_labels(self):
        with patch.object(tk.Label, "config") as mocked_method:
            self.app.update_labels()
        self.assertEqual(mocked_method.call_count, 5)

    # Testing whether the GUI gets drawn or not
    def test_draw_network(self):
        with patch.object(nx, "draw") as mocked_method:
            self.app.draw_network()
        mocked_method.assert_called()

    # Testing whether the setter and getter methods work correctly
    def test_node_setter_getter(self):
        node = Node(1, 1000, {2: 200})
        self.assertEqual(node.equity, 1000)
        self.assertEqual(node.debts, {2: 200})
        node.equity = 2000
        node.debts = {3: 400}
        self.assertEqual(node.equity, 2000)
        self.assertEqual(node.debts, {3: 400})

    # Testing whether the nodes' colours represent their default status
    def test_node_default_status_and_colour(self):
        node = Node(1, 1000, {2: 1200})
        self.assertTrue(node.defaulted)
        self.assertEqual(node.colour, 'red')
        node.equity = 1300
        self.assertFalse(node.defaulted)
        self.assertEqual(node.colour, 'green')

    # Testing whether the EisenbergNoe class has any effect or not
    def test_eisenberg_noe_apply(self):
        initial_network_state = copy.deepcopy(self.network)
        eisenberg_noe = EisenbergNoe(self.network)
        eisenberg_noe.apply()
        self.assertNotEqual(initial_network_state, self.network)

    # Testing whether the Compression class has any effect or not
    def test_compression_apply(self):
        initial_network_state = copy.deepcopy(self.network)
        compression = Compression(self.network)
        compression.apply()
        self.assertNotEqual(initial_network_state, self.network)

    # Testing whether the pareto improvement returns true or false
    def test_is_pareto_improvement(self):
        eisenberg_noe = EisenbergNoe(self.network)
        eisenberg_noe.apply()
        self.assertIsInstance(eisenberg_noe.is_pareto_improvement(), bool)


if __name__ == '__main__':
    unittest.main()
