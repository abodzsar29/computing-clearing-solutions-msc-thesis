# Standard libraries
import logging
import copy

# Project modules
# from network import Network # Not strictly needed

class Compression:
    """Applies bilateral debt netting/compression to the network."""
    def __init__(self, network):
        self.network = network

    def apply(self):
        """Simplifies mutual debts for all pairs of nodes in the network."""
        logging.info("Applying debt compression/netting...")
        nodes = self.network.nodes
        processed_pairs = set() # Track processed pairs

        for i in range(len(nodes)):
            node_i = nodes[i]
            for j in range(i + 1, len(nodes)): # Check unique pairs
                node_j = nodes[j]
                pair = tuple(sorted((node_i.id, node_j.id)))

                if pair not in processed_pairs:
                    self.simplify_mutual_debt(node_i, node_j)
                    processed_pairs.add(pair)

        # Update node statuses after all simplifications
        for node in nodes:
             node.update_color()
        logging.info("Compression finished.")

    def simplify_mutual_debt(self, node_a, node_b):
        """Simplifies debt between two specific nodes if it's mutual."""
        a_owes_b_amount = node_a.debts.get(node_b.id, 0)
        b_owes_a_amount = node_b.debts.get(node_a.id, 0)

        # Only proceed if both debts are significant
        if a_owes_b_amount > 1e-9 and b_owes_a_amount > 1e-9:
            logging.debug(f"Compressing mutual debt between {node_a.id} and {node_b.id}: A owes {a_owes_b_amount:.2f}, B owes {b_owes_a_amount:.2f}")
            netting_amount = min(a_owes_b_amount, b_owes_a_amount)

            new_a_owes_b = a_owes_b_amount - netting_amount
            new_b_owes_a = b_owes_a_amount - netting_amount

            # Update Node A's debts
            if new_a_owes_b <= 1e-9:
                if node_b.id in node_a.debts: del node_a.debts[node_b.id]
                if self.network.graph.has_edge(node_a.id, node_b.id):
                    self.network.graph.remove_edge(node_a.id, node_b.id)
                    logging.debug(f"Removed edge {node_a.id}->{node_b.id}")
            else:
                node_a.debts[node_b.id] = new_a_owes_b

            # Update Node B's debts
            if new_b_owes_a <= 1e-9:
                if node_a.id in node_b.debts: del node_b.debts[node_a.id]
                if self.network.graph.has_edge(node_b.id, node_a.id):
                    self.network.graph.remove_edge(node_b.id, node_a.id)
                    logging.debug(f"Removed edge {node_b.id}->{node_a.id}")
            else:
                node_b.debts[node_a.id] = new_b_owes_a