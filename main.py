import threading
import queue
import time
import os
import matplotlib.pyplot as plt
from src.vrptw import VRPTWInstance
from src.visualization import plot_routes
from src.genetic_alg import evolve

plot_queue = queue.Queue()

def main():
    instance_names = ["C108", "C203", "C249", "C266", "R146", "R202", "RC207"]
    results = []

    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    for name in instance_names:
        res = run_ga_on_instance(
            instance_name=name,
            generations=100,
            population_size=50,
            save_dir=output_dir,
        )
        results.append(res)

    print("Finished all GA experiments.")

def run_ga(customers, depot):
    evolve(generations=100, customers=customers, depot=depot, plot_queue=plot_queue)

def save_route_plot(instance_name, customers, depot, routes, best_distance, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    plt.figure()
    plot_routes(
        customers=customers,
        depot=depot,
        routes=routes,
        generation=None,
        best_distance=best_distance,
    )
    out_path = os.path.join(save_dir, f"{instance_name}_best_routes.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

    print(f"Saved route plot for {instance_name} to {out_path}")

VEHICLES = {
    "C108": 11,
    "C203": 11,
    "C249": 11,
    "C266": 11,
    "R146": 10,
    "R202": 10,
    "RC207": 10,
}

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

    coords = [tuple(depot)] + list(
        customers[["x", "y"]].itertuples(index=False, name=None)
    )

    stats = []
    total_time = 0.0
    total_edges = 0

    for route in routes:
        prev = 0
        t = 0.0
        distance = 0.0

        for customer_idx in route:
            coord_idx = customer_idx + 1

            x1, y1 = coords[prev]
            x2, y2 = coords[coord_idx]
            d = hypot(x1 - x2, y1 - y2)

            distance += d
            t += d

            row = customers.iloc[customer_idx]
            ready = row["ready_time"]
            due = row["due_date"]
            service = row["service"]

            if t < ready:
                t = ready

            t += service
            prev = coord_idx
            total_edges += 1

        x1, y1 = coords[prev]
        x2, y2 = coords[0]
        d = hypot(x1 - x2, y1 - y2)
        distance += d
        t += d
        total_edges += 1

        stats.append(
            {
                "route": route,
                "length": len(route) + 1,
                "time": t,
                "distance": distance,
            }
        )

        total_time += t

    return stats, total_edges, total_time

def run_ga_on_instance(instance_name, generations=100, population_size=50, save_dir=None):
    filename = FILES[instance_name]
    inst = VRPTWInstance(filename)
    customers, depot = inst.customers, inst.depot

    num_vehicles = VEHICLES[instance_name]

    start = time.time()
    best = evolve(
        generations=generations,
        customers=customers,
        depot=depot,
        plot_queue=None,
        population_size=population_size,
        num_vehicles=num_vehicles,
    )
    duration = time.time() - start

    routes = best["routes"]
    route_stats, total_edges, total_time = compute_route_stats(routes, customers, depot)

    print(f"GA results for {instance_name}:")
    print(f"Duration: {duration:.3f}(s)")
    print("Route #, Route Length, Route Time")
    for i, r in enumerate(route_stats, start=1):
        print(f"{i}, {r['length']}, {r['time']:.2f}")
    print(f"Totals: {total_edges}, {total_time:.2f}\n")

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