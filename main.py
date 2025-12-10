import threading
import queue
import time
import os
import matplotlib.pyplot as plt
from src.vrptw import VRPTWInstance
from src.visualization import plot_routes
from src.genetic_alg import evolve

# Initialize plot queue
plot_queue = queue.Queue()

def main():
    """
    Main function to run, starts the GA and runs automatically on all instances, saves to result array
    """
    # Set instance names up in array
    instance_names = ["C108", "C203", "C249", "C266", "R146", "R202", "RC207"]
    # Initialize results array
    results = []

    # Creat and Initialize output directory
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over instances
    for name in instance_names:
        # Run the GA on each instance
        res = run_ga_on_instance(
            instance_name=name,
            generations=100,
            population_size=50,
            save_dir=output_dir,
        )
        results.append(res)

    print("Finished all GA experiments.")

def run_ga(customers, depot):
    """
    Helper function to run the genetic algorithm on a single instance (Used for testing)
    """
    evolve(generations=100, customers=customers, depot=depot, plot_queue=plot_queue)

def save_route_plot(instance_name, customers, depot, routes, best_distance, save_dir):
    """
    Helper function to save the final routes as a plot for later analysis and data collection
    """
    # Create directory to save file if it does not exist
    os.makedirs(save_dir, exist_ok=True)

    # Plot the routes
    plt.figure()
    plot_routes(
        customers=customers,
        depot=depot,
        routes=routes,
        generation=None,
        best_distance=best_distance,
    )
    # Generate filename, save file, then close the plot
    out_path = os.path.join(save_dir, f"{instance_name}_best_routes.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

    print(f"Saved route plot for {instance_name} to {out_path}")

# Number of vehicles per instance
VEHICLES = {
    "C108": 11,
    "C203": 11,
    "C249": 11,
    "C266": 11,
    "R146": 10,
    "R202": 10,
    "RC207": 10,
}

# Filepaths for data
FILES = {
    "C108": "data/c108.txt",
    "C203": "data/c203.txt",
    "C249": "data/c249.txt",
    "C266": "data/c266.txt",
    "R146": "data/r146.txt",
    "R202": "data/r202.txt",
    "RC207": "data/rc207.txt",
}

def compute_route_stats(routes, customers, depot):
    from math import hypot

    # Storing coordinates in a list
    coords = [tuple(depot)] + list(
        customers[["x", "y"]].itertuples(index=False, name=None)
    )

    # Initialization of parameters
    stats = []
    total_time = 0.0
    total_edges = 0

    # Iterate over the routes
    for route in routes:
        # Reset/Initialize parameters
        prev = 0
        t = 0.0
        distance = 0.0

        # Iterate over customers in a route
        for customer_idx in route:
            # Extracting coordinates and calculating distance
            coord_idx = customer_idx + 1

            x1, y1 = coords[prev]
            x2, y2 = coords[coord_idx]
            d = hypot(x1 - x2, y1 - y2)

            # Summation of distances
            distance += d
            t += d

            # Extracting customer details
            row = customers.iloc[customer_idx]
            ready = row["ready_time"]
            due = row["due_date"]
            service = row["service"]

            # If early move time forward
            if t < ready:
                t = ready

            # Service wait time
            t += service
            # Save previous index to help in continuation
            prev = coord_idx
            # Increase edge count
            total_edges += 1

        # Extract coordinates from data structure
        x1, y1 = coords[prev]
        x2, y2 = coords[0]
        # Calculate distance
        d = hypot(x1 - x2, y1 - y2)
        distance += d
        # Calculate total distance
        t += d
        # Increase edge count
        total_edges += 1

        # Add results to stats list
        stats.append(
            {
                "route": route,
                "length": len(route) + 1,
                "time": t,
                "distance": distance,
            }
        )

        # Increase add current time taken to total time
        total_time += t

    return stats, total_edges, total_time

def run_ga_on_instance(instance_name, generations=100, population_size=50, save_dir=None):
    """
    Helper function to run the GA on an instance of data
    """
    # Parameter initialization
    filename = FILES[instance_name]
    inst = VRPTWInstance(filename)
    customers, depot = inst.customers, inst.depot
    num_vehicles = VEHICLES[instance_name]

    # Start the timer for recording
    start = time.time()
    # Save the best routes/individuals
    best = evolve(
        generations=generations,
        customers=customers,
        depot=depot,
        plot_queue=None,
        population_size=population_size,
        num_vehicles=num_vehicles,
    )
    # Calculate computation time
    duration = time.time() - start

    # Save the best routes
    routes = best["routes"]
    # Compute route stats
    route_stats, total_edges, total_time = compute_route_stats(routes, customers, depot)

    # Output results to terminal
    print(f"GA results for {instance_name}:")
    print(f"Duration: {duration:.3f}(s)")
    print("Route #, Route Length, Route Time")
    for i, r in enumerate(route_stats, start=1):
        print(f"{i}, {r['length']}, {r['time']:.2f}")
    print(f"Totals: {total_edges}, {total_time:.2f}\n")

    # Save plot
    if save_dir is not None:
        save_route_plot(
            instance_name=instance_name,
            customers=customers,
            depot=depot,
            routes=routes,
            best_distance=best["distance"],
            save_dir=save_dir,
        )

    return {
        "instance": instance_name,
        "duration": duration,
        "routes": route_stats,
        "total_length": total_edges,
        "total_time": total_time,
    }

if __name__ == '__main__':

    main()

