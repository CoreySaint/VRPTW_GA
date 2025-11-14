import time
import random
from src.visualization import plot_routes, is_paused, should_stop

def evolve(generations, customers, depot, plot_queue):
    for gen in range(generations):
        if should_stop.is_set():
            print("GA stopped early.")
            break

        while is_paused.is_set():
            time.sleep(0.1)

        best_routes = [random.sample(range(len(customers)), 10)]  # dummy
        best_distance = 120.5 - gen  # dummy decreasing distance

        plot_queue.put({
            "customers": customers,
            "depot": depot,
            "routes": best_routes,
            "generation": gen,
            "best_distance": best_distance
        })

        time.sleep(0.3)

    print("GA complete.")
