# VRPTW_GA
## Prerequisites:
- Python 3.13
- Python standard library
  - Math
  - Time
  - Random
  - Threading
  - Queue
- Matplotlib package
- Pandas package
- Numpy package
## Data
- Data consists of Solomon VRPTW datasets collected from: https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/
## How to run:
1. Install requirements
   `pip install requirements.txt`
3. Ensure you have Solomon datasets in data folder
4. Run main.py
   `run main.py`
## Parameters
1. Instances:
   - C108.txt
   - C203.txt
   - C249.txt
   - C266.txt
   - R146.txt
   - R202.txt
   - RC207.txt
3. Genetic Algorithm Parameters
   - Generations: 100
   - Population size: 50
   - Vehicles: 11
   - Mutation rate: 20%
   - Crossover rate: 80%
   - Top N = 40%
## Example Output
![](./figures/C108_best_routes.png "Plot Output")
