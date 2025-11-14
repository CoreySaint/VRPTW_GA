import threading
import queue
import time
from src.vrptw import VRPTWInstance
from src.visualization import start_visualization, plot_routes, close_plot
from src.genetic_alg import evolve

plot_queue = queue.Queue()

def main():
    instance = VRPTWInstance('data/c101.txt')

    ga_thread = threading.Thread(target=run_ga, args=(instance.customers, instance.depot))
    ga_thread.start()

    start_visualization(instance.customers, instance.depot)
    while ga_thread.is_alive():
        try:
            data = plot_queue.get(timeout=0.1)
            if data is None:
                break
            plot_routes(**data)
        except queue.Empty:
            pass
        time.sleep(0.1)
    close_plot()

def run_ga(customers, depot):
    evolve(generations=100, customers=customers, depot=depot, plot_queue=plot_queue)

if __name__ == '__main__':
    main()