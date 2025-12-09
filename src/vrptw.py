import pandas as pd
import numpy as np
import math

class VRPTWInstance:
    def __init__(self, filepath):
        """
        Initialization of the filepath, parsing of data, and creation of distance matrix
        """
        self.filepath = filepath
        self.customers, self.depot, self.capacity = self._parse_solomon(filepath)
        self.distance_matrix = self._compute_distance_matrix()

    def _parse_solomon(self, path):
        """
        Helper function to open the file and insert into dataframe
        """
        # Open the file path in read mode and iterate through lines
        with open(path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        capacity = int(lines[3].split()[-1])
        # Convert read data into dataframe of file information
        df = pd.DataFrame([list(map(float, l.split())) for l in lines[6:]], 
                          columns=['cust_no', 'x', 'y', 'demand', 'ready_time', 'due_date', 'service'])
        # Set depot dataframe from file information dataframe
        depot = df.iloc[0][['x', 'y']].values
        # Set customers dataframe from file information dataframe
        customers = df.iloc[1:].reset_index(drop=True)
        # Convert customer numbers from string to integer
        customers['cust_no'] = customers['cust_no'].astype(int)

        return customers, depot, capacity
    
    def _compute_distance_matrix(self):
        """
        Helper function to create a distance matrix from all the points in the read file
        """
        # Get coordinates from dataframe and convert to list
        coords = [self.depot] + self.customers[['x', 'y']].values.tolist()
        # Get number of customers
        n = len(coords)
        # Create empty matrix of size n x n
        distance_matrix = np.zeros((n, n))
        # Iterate over the coordinates to fill matrix
        for i in range(n):
            for j in range(n):
                # Distance calculation
                distance_matrix[i, j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])

        return distance_matrix
