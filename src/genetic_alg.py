import math
import random
import time
from .visualization import is_paused, should_stop

def build_distance_matrix(customers, depot):
    coords = [tuple(depot)] + [
        (row["x"], row["y"]) for _, row in customers.iterrows()
    ]
    n = len(coords)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        x1, y1 = coords[i]
        for j in range(n):
            x2, y2 = coords[j]
            dist[i][j] = math.hypot(x1 - x2, y1 - y2)
    return dist

def split_into_routes(order, num_vehicles):
    n = len(order)
    base = n // num_vehicles
    extra = n % num_vehicles
    routes = []
    idx = 0

    for v in range(num_vehicles):
        size = base + (1 if v < extra else 0)
        routes.append(order[idx:idx + size])
        idx += size

    return routes

def evaluate(routes, customers, dist_matrix, penalty=1000.0):
    total_distance = 0.0
    total_lateness = 0.0

    for route in routes:
        prev = 0
        time_here = 0.0

        for customer_idx in route:
            coord_idx = customer_idx + 1
            d = dist_matrix[prev][coord_idx]
            total_distance += d
            time_here += d

            row = customers.iloc[customer_idx]
            ready = row["ready_time"]
            due = row["due_date"]
            service = row["service"]

            if time_here < ready:
                time_here = ready

            if time_here > due:
                total_lateness += time_here - due

            time_here += service
            prev = coord_idx

        d = dist_matrix[prev][0]
        total_distance += d
        time_here += d

    fitness = total_distance + penalty * total_lateness
    
    return fitness, total_distance

def order_crossover(parent1, parent2):
    n = len(parent1)
    if n < 2:
        return parent1[:], parent2[:]

    i, j = sorted(random.sample(range(n), 2))
    child1 = [None] * n
    child2 = [None] * n

    child1[i:j + 1] = parent1[i:j + 1]
    child2[i:j + 1] = parent2[i:j + 1]

    def fill(child, other):
        idx = (j + 1) % n
        for gene in other[j + 1:] + other[:j + 1]:
            if gene not in child:
                while child[idx] is not None:
                    idx = (idx + 1) % n
                child[idx] = gene
        return child

    child1 = fill(child1, parent2)
    child2 = fill(child2, parent1)

    return child1, child2

def mutate(routes, mutation_rate):
    new_routes = [r[:] for r in routes]

    for route in new_routes:
        if len(route) >= 2 and random.random() < mutation_rate:
            i = random.randrange(len(route) - 1)
            route[i], route[i + 1] = route[i + 1], route[i]

    return new_routes

def evolve(generations, customers, depot, plot_queue=None, population_size=50, num_vehicles=None, crossover_rate=0.8, mutation_rate=0.2, top_n_fraction=0.4):
    num_customers = len(customers)
    if num_vehicles is None:
        num_vehicles = max(1, num_customers // 10)

    dist_matrix = build_distance_matrix(customers, depot)

    population = []
    for _ in range(population_size):
        order = random.sample(range(num_customers), num_customers)
        routes = split_into_routes(order, num_vehicles)
        fitness, dist = evaluate(routes, customers, dist_matrix)
        population.append({"routes": routes, "fitness": fitness, "distance": dist})

    population.sort(key=lambda s: s["fitness"])
    best = population[0]

    if plot_queue is not None:
        plot_queue.put({
            "customers": customers,
            "depot": depot,
            "routes": best["routes"],
            "generation": 0,
            "best_distance": best["distance"],
        })

    top_n = max(2, int(population_size * top_n_fraction))

    for gen in range(1, generations + 1):
        if should_stop.is_set():
            break

        while is_paused.is_set():
            time.sleep(0.1)

        new_population = []

        new_population.append({
            "routes": [r[:] for r in best["routes"]],
            "fitness": best["fitness"],
            "distance": best["distance"],
        })

        parents_pool = population[:top_n]

        while len(new_population) < population_size:
            parent1 = random.choice(parents_pool)
            parent2 = random.choice(parents_pool)

            flat1 = [c for route in parent1["routes"] for c in route]
            flat2 = [c for route in parent2["routes"] for c in route]

            if random.random() < crossover_rate:
                child_order1, child_order2 = order_crossover(flat1, flat2)
            else:
                child_order1, child_order2 = flat1[:], flat2[:]

            for child_order in (child_order1, child_order2):
                if len(new_population) >= population_size:
                    break

                routes = split_into_routes(child_order, num_vehicles)
                routes = mutate(routes, mutation_rate)
                fitness, dist = evaluate(routes, customers, dist_matrix)
                new_population.append({
                    "routes": routes,
                    "fitness": fitness,
                    "distance": dist,
                })

        population = sorted(new_population, key=lambda s: s["fitness"])
        gen_best = population[0]

        if gen_best["fitness"] < best["fitness"]:
            best = gen_best

        if plot_queue is not None:
            plot_queue.put({
                "customers": customers,
                "depot": depot,
                "routes": best["routes"],
                "generation": gen,
                "best_distance": best["distance"],
            })

    print("GA Completed.")
    
    return best