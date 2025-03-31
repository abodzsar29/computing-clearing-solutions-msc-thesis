# Standard libraries
import logging
import copy

class Node:
    """Represents a single financial entity (node) in the network."""
    # Constructor of the class, called when an object of the class is initialized
    def __init__(self, id, equity, debts):
        self.id = id  # Assigns the provided id to the instance
        self._equity = equity # Use protected attribute
        self.initial_equity = equity  # Stores the initial equity value for reset
        self._debts = debts # Use protected attribute
        self.initial_debts = copy.deepcopy(debts)  # Stores a deep copy of initial debts for reset
        self.update_color() # Initial calculation of defaulted status and color

    # Creates a getter for the private variable _equity
    @property
    def equity(self):
        """Gets the current equity of the node."""
        return self._equity

    # Creates a setter for the private variable _equity
    @equity.setter
    def equity(self, value):
        """Sets the equity and updates node status."""
        self._equity = value
        self.update_color()  # Calls the update_color method after the equity is changed

    # Creates a getter for the private variable _debts
    @property
    def debts(self):
        """Gets the current debts dictionary (creditor_id: amount_owed)."""
        return self._debts

    # Creates a setter for the private variable _debts
    @debts.setter
    def debts(self, value):
        """Sets the debts dictionary and updates node status."""
        # Ensure value is a dictionary if setting directly
        if not isinstance(value, dict):
             raise TypeError("Debts must be a dictionary.")
        self._debts = value
        self.update_color()  # Calls the update_color method after the debts are changed

    # Calculates and returns the total debt
    def total_debt(self):
        """Calculates the total amount owed by this node."""
        return sum(self._debts.values())

    # Resets the node's equity and debts to their initial values and updates the color
    def reset(self):
        """Resets the node to its initial equity and debts."""
        self.equity = self.initial_equity  # Resets the equity (uses setter)
        self.debts = copy.deepcopy(self.initial_debts)  # Resets the debts (uses setter)
        # update_color is called implicitly by setters

    # Checks the defaulted state and updates the color accordingly
    def update_color(self):
        """Updates the node's defaulted status and color based on current equity and debt."""
        current_equity = self.equity
        current_total_debt = self.total_debt()
        self.defaulted = current_equity < current_total_debt
        self.colour = 'red' if self.defaulted else 'green'