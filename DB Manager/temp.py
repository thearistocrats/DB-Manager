import math
import pandas as pd

class FunctionTable:
    def __init__(self, func, max_N, max_M):
        """
        func : callable, the function y(x)
        max_N : int, maximum n value
        max_M : int, maximum m value
        """
        self.func = func
        self.max_N = max_N
        self.max_M = max_M
        self.table = None

    def build_table(self):
        """Constructs the table and stores it as a pandas DataFrame."""
        data = []
        for n in range(self.max_N):
            row = []
            for m in range(self.max_M):
                row.append(n+1 * self.func(m+1))
            data.append(row)

        self.table = pd.DataFrame(
            data,
            index=[f"n={n + 1}" for n in range(self.max_N)],
            columns=[f"m={m + 1}" for m in range(self.max_M)]
        )
        return self.table

    def display(self):
        """Prints the table (builds it if needed)."""
        if self.table is None:
            self.build_table()
        print(self.table)

    def save_csv(self, filename="table.csv"):
        """Saves the table to a CSV file."""
        if self.table is None:
            self.build_table()
        self.table.to_csv(filename, index=True)
