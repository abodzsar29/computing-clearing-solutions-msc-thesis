import random
import logging
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import copy
import pandas as pd
import os
from networkgraph import NetworkGraph


class Simulation:
    def __init__(self, app):
        self.app = app
        self.results_df = pd.DataFrame(columns=[
            'EN Change in Debt',
            'EN Survived Nodes Change', 'EN Defaulted Nodes Change',
            'EN Pareto Improvement',
            'Compression+EN Change in Debt',
            'Compression+EN Survived Nodes Change',
            'Compression+EN Defaulted Nodes Change',
            'Compression+EN Pareto Improvement'
        ])

    def run(self):
        for _ in range(10):
            initial_data = {
                'Total Debt': self.app.network.total_network_debt(),
                'Survived Nodes': self.app.network.survived_nodes_count(),
                'Defaulted Nodes': self.app.network.defaulted_nodes_count()
            }

            self.app.reset()
            self.app.eisenberg_noe_apply()
            en_data = {
                'Change in Debt': self.app.network.total_network_debt() -
                                  initial_data['Total Debt'],
                'Survived Nodes Change': self.app.network.survived_nodes_count() -
                                         initial_data['Survived Nodes'],
                'Defaulted Nodes Change': self.app.network.defaulted_nodes_count() -
                                          initial_data['Defaulted Nodes'],
                'Pareto Improvement': 'Yes' if
                self.app.pareto_improvement_label.cget("text").split(": ")[
                    1] == 'Yes' else 'No'
            }

            self.app.reset()
            self.app.compression_apply()
            self.app.eisenberg_noe_apply()
            compression_en_data = {
                'Change in Debt': self.app.network.total_network_debt() -
                                  initial_data['Total Debt'],
                'Survived Nodes Change': self.app.network.survived_nodes_count() -
                                         initial_data['Survived Nodes'],
                'Defaulted Nodes Change': self.app.network.defaulted_nodes_count() -
                                          initial_data['Defaulted Nodes'],
                'Pareto Improvement': 'Yes' if
                self.app.pareto_improvement_label.cget("text").split(": ")[
                    1] == 'Yes' else 'No'
            }

            row_data = {
                **{'EN ' + k: v for k, v in en_data.items()},
                **{'Compression+EN ' + k: v for k, v in
                   compression_en_data.items()}
            }
            self.results_df = self.results_df.append(row_data,
                                                     ignore_index=True)

            self.app.new_graph()

        # Calculate the desired metrics after 100 simulations
        summary_data = {
            'Avrg EN Change in Debt': self.results_df[
                'EN Change in Debt'].mean(),
            'Avrg EN+C Change in Debt': self.results_df[
                'Compression+EN Change in Debt'].mean(),

            'Avrg EN Survived Nodes Change': self.results_df[
                'EN Survived Nodes Change'].mean(),
            'Avrg EN+C Survived Nodes Change': self.results_df[
                'Compression+EN Survived Nodes Change'].mean(),

            'Avrg EN Defaulted Nodes Change': self.results_df[
                'EN Defaulted Nodes Change'].mean(),
            'Avrg EN+C Defaulted Nodes Change': self.results_df[
                'Compression+EN Defaulted Nodes Change'].mean(),

            'EN Pareto Improvement Yes': self.results_df[
                'EN Pareto Improvement'].value_counts().get('Yes', 0),
            'EN+C Pareto Improvement Yes': self.results_df[
                'Compression+EN Pareto Improvement'].value_counts().get('Yes',
                                                                        0),

            'EN Pareto Improvement No': self.results_df[
                'EN Pareto Improvement'].value_counts().get('No', 0),
            'EN+C Pareto Improvement No': self.results_df[
                'Compression+EN Pareto Improvement'].value_counts().get('No', 0)
        }

        summary_df = pd.DataFrame([summary_data])

        # Check if the file exists
        if os.path.exists('summary_results.xlsx'):
            # Read the existing data
            existing_data = pd.read_excel('summary_results.xlsx')
            # Append the new data
            summary_df = pd.concat([existing_data, summary_df], ignore_index=True)

        # Create file and save the summary
        summary_df.to_excel('summary_results.xlsx', index=False)

        # Code for printing simulation results
        print("Printing Individual Run Data -------------------")
        print(self.results_df)
        print("Printing Summary Data --------------------------")
        print(summary_df)