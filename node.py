import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os


class Node:
    # Constructor of the class, called when an object of the class is initialized
    def __init__(self, id, equity, debts):
        self.id = id  # Assigns the provided id to the instance
        self._equity = equity
        self.initial_equity = equity  # Stores the initial equity value for potential later use
        self._debts = debts
        self.initial_debts = copy.deepcopy(debts)  # Stores a deep copy of the initial debts dictionary for potential later use
        self.defaulted = self.equity < self.total_debt()  # Calculates if the node has defaulted, i.e., if debts exceed equity
        self.colour = 'red' if self.defaulted is True else 'green'  # Node's colour is set to red if it has defaulted, otherwise to green
        self.totaldebt = self.total_debt()  # Calculates the total debt of the node
        self.update_color()  # Calls the update_colour method to set the color based on the node's financial status

    # Creates a getter for the private variable _equity
    @property
    def equity(self):
        return self._equity  # Returns the value of private variable _equity

    # Creates a setter for the private variable _equity
    @equity.setter
    def equity(self, value):
        self._equity = value
        self.update_color()  # Calls the update_color method after the equity is changed

    # Creates a getter for the private variable _debts
    @property
    def debts(self):
        return self._debts  # Returns the value of private variable _debts.

    # Creates a setter for the private variable _debts
    @debts.setter
    def debts(self, value):
        self._debts = value
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