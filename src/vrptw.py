import pandas as pd
import numpy as np
import math

class VRPTWInstance:
    def __init__(self, filepath):
        self.filepath = filepath
        self.customers, self.depot, self.capacity = self._parse_solomon(filepath)
        self.distance_matrix = self._compute_distance_matrix()

    def _parse_solomon(self, path):
        with open(path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        capacity = int(lines[3].split()[-1])
        df = pd.DataFrame([list(map(float, l.split())) for l in lines[6:]], 
                          columns=['cust_no', 'x', 'y', 'demand', 'ready_time', 'due_date', 'service'])
        depot = df.iloc[0][['x', 'y']].values
        customers = df.iloc[1:].reset_index(drop=True)
        customers['cust_no'] = customers['cust_no'].astype(int)

        return customers, depot, capacity
    
    def _compute_distance_matrix(self):
        coords = [self.depot] + self.customers[['x', 'y']].values.tolist()
        n = len(coords)
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distance_matrix[i, j] = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])
        return distance_matrix