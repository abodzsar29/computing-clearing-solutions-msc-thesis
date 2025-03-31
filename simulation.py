# Standard libraries
import logging
import os
import copy

# Third-party libraries
import pandas as pd
import tkinter as tk
import networkx as nx
# Project modules
from networkgraph import NetworkGraph


class Simulation:
    def __init__(self, app):
        self.app = app # The NetworkGraph application instance
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
        results_list = []  # Accumulate rows for concat
        for _ in range(10): # Run 10 iterations/graphs
            # --- Get initial state of the current graph ---
            current_network = self.app.network
            initial_data = {
                'Total Debt': current_network.total_network_debt(),
                'Survived Nodes': current_network.survived_nodes_count(),
                'Defaulted Nodes': current_network.defaulted_nodes_count()
            }

            # --- Run Eisenberg-Noe Only ---
            self.app.reset() # Reset to initial state of the current graph
            self.app.eisenberg_noe_apply() # Apply EN
            en_data = {
                'Change in Debt': current_network.total_network_debt() -
                                  initial_data['Total Debt'],
                'Survived Nodes Change': current_network.survived_nodes_count() -
                                         initial_data['Survived Nodes'],
                'Defaulted Nodes Change': current_network.defaulted_nodes_count() -
                                          initial_data['Defaulted Nodes'],
                'Pareto Improvement': 'Yes' if self.app.last_pareto_status else 'No'
            }

            # --- Run Compression + Eisenberg-Noe ---
            self.app.reset() # Reset to initial state of the current graph
            self.app.compression_apply() # Apply Compression
            self.app.eisenberg_noe_apply() # Apply EN after Compression
            compression_en_data = {
                'Change in Debt': current_network.total_network_debt() -
                                  initial_data['Total Debt'],
                'Survived Nodes Change': current_network.survived_nodes_count() -
                                         initial_data['Survived Nodes'],
                'Defaulted Nodes Change': current_network.defaulted_nodes_count() -
                                          initial_data['Defaulted Nodes'],
                'Pareto Improvement': 'Yes' if self.app.last_pareto_status else 'No'
            }

            # --- Store results for this iteration ---
            row_data = {
                **{'EN ' + k: v for k, v in en_data.items()},
                **{'Compression+EN ' + k: v for k, v in
                   compression_en_data.items()}
            }
            results_list.append(row_data) # Add row data to list

            # --- Generate a new graph for the next iteration ---
            self.app.new_graph()

        # --- Aggregate results after all iterations ---
        new_results_df = pd.DataFrame(results_list)
        self.results_df = pd.concat([self.results_df, new_results_df], ignore_index=True)

        # --- Calculate summary metrics over the 10 runs ---
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

        # --- Save summary results ---
        output_filename = 'summary_results.xlsx'
        try:
            # Check if the file exists
            if os.path.exists(output_filename):
                # Read the existing data
                existing_data = pd.read_excel(output_filename)
                # Append the new data
                summary_df = pd.concat([existing_data, summary_df], ignore_index=True)

            # Create file and save the summary
            summary_df.to_excel(output_filename, index=False)
            logging.info(f"Summary results saved to {output_filename}")

        except Exception as e:
            logging.error(f"Failed to save summary results to Excel: {e}")

        # --- Print results to console ---
        print("\nPrinting Individual Run Data (Last 10 Runs) -------------------")
        print(self.results_df.tail(10).to_string())
        print("\nPrinting Summary Data (From Excel File) --------------------------")
        print(summary_df.to_string())