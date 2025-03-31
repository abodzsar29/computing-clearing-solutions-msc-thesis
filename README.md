# Computing Clearing Solutions in Financial Networks Project

Welcome! This document provides instructions for the project by Andrew Bodzsar, submitted for the MSc Computational Finance at King's College London.

## Project Overview

This project implements a financial network model allowing the application and comparison of two distinct algorithms:

1.  **Eisenberg & Noe (2001) Clearing Algorithm:** Determines the final state of debts and equities in a network by iteratively settling obligations based on available funds until a stable state (fixed point) is reached.
2.  **Schuldenzucker & Seuken Compression Algorithm:** A bilateral netting algorithm that simplifies the debt structure by canceling out offsetting debts between pairs of nodes *before* clearing.

The primary goal is to analyze and compare the impact of these algorithms (specifically, applying Eisenberg-Noe directly versus applying Compression *followed by* Eisenberg-Noe) on key network metrics:
*   Overall network equity and debt levels.
*   The number of solvent ("alive") nodes versus defaulted nodes.

The `Run Simulation` feature automates this comparison over multiple randomly generated networks, providing average results.

---

## How to Run the Program

Execute the `main.py` file using a Python 3 interpreter. Navigate to the project directory in your terminal and run:

```bash
python main.py
```

The project was developed using PyCharm.

### Dependencies can be found in the requirements.txt file

---

## GUI Overview

Running `main.py` opens a Tkinter GUI displaying a visualization of the financial network. Nodes (financial entities) are represented by circles (Red=Defaulted, Green=Solvent).

### Node Information (Labels on/near nodes)

*   **ID:** Unique identifier for the node.
*   **Equity:** Current equity held by the node. *Note: Receivables (money owed to this node) are not included until paid during clearing.*
*   **Debt:** Total amount this node owes to others.
*   **Defaulted:** Node status:
    *   `True` (Red Node): Owes more than its current equity.
    *   `False` (Green Node): Has sufficient equity for immediate debts.

### Network Statistics (Labels at top/bottom)

*   **Total Equity:** Sum of equity across all nodes.
*   **Total Debt:** Sum of all outstanding debts in the network.
*   **Defaulted Nodes:** Current count of nodes with `Defaulted: True`.
*   **Survived Nodes:** Current count of nodes with `Defaulted: False`.
*   **Pareto Improvement:** Indicates if the last Eisenberg-Noe run was Pareto-improving (`Yes`/`No`/`-`). A 'Yes' means no node's final equity was lower than its equity *before* that specific clearing process started.

### Edges (Arrows between nodes)

*   An arrow points from the **debtor** (tail) to the **creditor** (head).
*   A double-headed arrow (or two distinct arrows A->B and B->A) signifies reciprocal debt.

---

## GUI Buttons

*   **`EisenbergNoe`:** Applies the Eisenberg & Noe (2001) clearing algorithm. Payments are made iteratively based on available equity until a fixed point is reached. Updates the network visualization and statistics.
*   **`Compression`:** Applies the bilateral netting algorithm (similar to Schuldenzucker & Seuken). Cancels out offsetting debts between pairs of nodes. Updates the network visualization (reciprocal arrows should disappear or reduce).
*   **`Reset`:** Resets the *currently displayed* network to its original state (as generated or loaded).
*   **`New Graph`:** Generates a completely new random financial network, displays it, and resets all statistics.
*   **`Run Simulation`:** Performs an automated comparison analysis:
    1.  Records initial metrics of the current graph.
    2.  Applies Eisenberg-Noe, records post-EN metrics.
    3.  Resets the graph to its initial state.
    4.  Applies Compression, then Eisenberg-Noe, records post-Compression+EN metrics.
    5.  Repeats steps 1-4 for a total of **10 iterations**, generating a *new graph* for each iteration after the first.
    6.  Prints the results for each of the 10 tests to the console.
    7.  Calculates and saves the **average** metrics over the 10 tests to `summary_results.xlsx`. Each click on `Run Simulation` appends a new row of average results to this file.
*   **`Quit`:** Closes the GUI and terminates the program.

---

## Simulation Output Metrics Explained

The metrics reported by the `Run Simulation` feature (both per-test in the console and averaged in `summary_results.xlsx`) measure the **change** from the initial state of each graph to the state after applying the specified algorithm(s).

*   **`EN Change in Debt`:** (Total Debt after EN) - (Initial Total Debt). Expected to be ≤ 0.
*   **`EN Survived Nodes Change`:** (Survived Nodes after EN) - (Initial Survived Nodes).
*   **`EN Defaulted Nodes Change`:** (Defaulted Nodes after EN) - (Initial Defaulted Nodes).
*   **`EN Pareto Improvement`:** `Yes` or `No`, indicating if the EN-only run for that graph resulted in a Pareto improvement.

*   **`Compression+EN Change in Debt`:** (Total Debt after Compression+EN) - (Initial Total Debt). Expected to be ≤ 0.
*   **`Compression+EN Survived Nodes Change`:** (Survived Nodes after Compression+EN) - (Initial Survived Nodes).
*   **`Compression+EN Defaulted Nodes Change`:** (Defaulted Nodes after Compression+EN) - (Initial Defaulted Nodes).
*   **`Compression+EN Pareto Improvement`:** `Yes` or `No`, indicating if the EN run *after compression* resulted in a Pareto improvement for that graph.

The `summary_results.xlsx` file stores the **average** values of these change metrics across the 10 graphs tested during each full simulation run initiated by clicking the `Run Simulation` button.
```
