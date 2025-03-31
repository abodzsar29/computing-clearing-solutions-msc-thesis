# Standard libraries
import logging
import copy

# Project modules
from network import Network

class EisenbergNoe:
    """Implements the Eisenberg & Noe (2001) clearing algorithm."""
    def __init__(self, network):
        if not isinstance(network, Network):
            raise TypeError("EisenbergNoe requires a Network object.")
        self.network = network
        # Store initial equities for Pareto check and change calculation
        self.initial_equities = {node.id: node.equity for node in network.nodes}

    def apply(self, max_iterations=100, tolerance=1e-9):
        """
        Applies the Eisenberg Noe model iteratively until convergence or max iterations.

        Args:
            max_iterations (int): Maximum number of iterations to prevent infinite loops.
            tolerance (float): Convergence tolerance for equity changes.
        """
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            equity_changed_significantly = False
            previous_equities = {node.id: node.equity for node in self.network.nodes}

            for node in self.network.nodes:
                self.clear_debts_for_node(node)

            # Check for convergence
            max_change = 0
            for node in self.network.nodes:
                change = abs(node.equity - previous_equities[node.id])
                max_change = max(max_change, change)
                if change > tolerance:
                    equity_changed_significantly = True

            if not equity_changed_significantly:
                logging.info(f"Eisenberg-Noe converged after {iteration} iterations.")
                break
        else: # max_iterations reached
             logging.warning(f"Eisenberg-Noe did not converge after {max_iterations} iterations. Max change: {max_change}")

        # Final state update
        logging.info("Finalizing node states post-clearing.")
        for node in self.network.nodes:
            # Enforce clearing conditions: if node has positive equity, it should have zero debt
            if node.equity > tolerance:
                node.debts = {}
                # Also remove outgoing edges in the graph
                for edge in list(self.network.graph.out_edges(node.id)):
                    self.network.graph.remove_edge(edge[0], edge[1])
                    
            node.equity = round(node.equity, 6)
            node.update_color()

    def is_pareto_improvement(self):
        """Checks if any node's equity decreased compared to its pre-clearing state."""
        for node in self.network.nodes:
            if node.equity < self.initial_equities[node.id] - 1e-9:
                logging.info(f"Node {node.id} worse off: Initial={self.initial_equities[node.id]:.2f}, Final={node.equity:.2f}. Not Pareto Improvement.")
                return False
        logging.info("No node worse off. Pareto Improvement achieved.")
        return True

    def clear_debts_for_node(self, node):
        """Calculates and distributes payments for a single node based on its current equity."""
        total_debt = node.total_debt()
        if total_debt <= 1e-9:
            return

        available_equity = node.equity
        if available_equity <= 1e-9:
             node.equity = 0
             return

        # Node pays proportionally up to its available equity
        payment_fraction = min(available_equity / total_debt, 1.0)

        debt_items = list(node.debts.items()) # Iterate over a copy
        total_paid_by_node = 0

        for creditor_id, owed in debt_items:
            payment = owed * payment_fraction
            actual_payment = round(payment, 6)

            if actual_payment > 1e-9:
                creditor = self.network.get_node_by_id(creditor_id)
                if creditor:
                    total_paid_by_node += actual_payment
                    creditor.equity += actual_payment

                    # Update debt amount owed by node
                    new_debt = node.debts[creditor_id] - actual_payment
                    if new_debt <= 1e-9:
                        del node.debts[creditor_id]
                        if self.network.graph.has_edge(node.id, creditor_id):
                            self.network.graph.remove_edge(node.id, creditor_id)
                            logging.debug(f"Debt cleared: {node.id} -> {creditor_id}. Edge removed.")
                    else:
                        node.debts[creditor_id] = new_debt
                else:
                    logging.warning(f"Node {node.id} trying to pay non-existent creditor {creditor_id}")

        node.equity -= total_paid_by_node
        # Ensure equity is not negative
        if node.equity < 0:
            node.equity = 0

        # Update node's color/status
        node.update_color()

    def node_equity_change(self):
        """Prints the change in equity for each node compared to its pre-clearing state."""
        print("\n--- Equity Changes Post Eisenberg-Noe ---")
        for node in self.network.nodes:
            change = node.equity - self.initial_equities[node.id]
            print(f'Node {node.id}: Initial Equity={self.initial_equities[node.id]:.2f}, Final Equity={node.equity:.2f}, Change={change:+.2f}')
        print("----------------------------------------")