import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import threading

is_paused = threading.Event()
is_paused.clear()
should_stop = threading.Event()
should_stop.clear()

def clear_previous_plot():
    plt.clf()

def plot_routes(customers, depot, routes, generation=None, best_distance=None):
    clear_previous_plot()

    plt.scatter([depot[0]], [depot[1]], c='red', marker='s', label='Depot', s=100)
    plt.scatter(customers['x'], customers['y'], c='blue', label='Customers')

    colors = plt.cm.get_cmap('tab10', len(routes))
    for i, route in enumerate(routes):
        route_x = [depot[0]] + [customers.iloc[c]['x'] for c in route] + [depot[0]]
        route_y = [depot[1]] + [customers.iloc[c]['y'] for c in route] + [depot[1]]
        plt.plot(route_x, route_y, color=colors(i), linewidth=2, label=f'Vehicle {i+1}')

    plt.title(f"Generation {generation + 1} | Best Distance: {best_distance:.2f}" if generation else "Initial Routes")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(loc='upper right')
    plt.pause(0.1)

def toggle_pause(event):
    if is_paused.is_set():
        is_paused.clear()
        print("Resumed")
    else:
        is_paused.set()
        print("Paused")

def stop_execution(event):
    should_stop.set()
    print("Stopped")

def buttons():
    ax_pause = plt.axes([0.7, 0.02, 0.1, 0.05])
    ax_stop = plt.axes([0.82, 0.02, 0.1, 0.05])

    btn_pause = Button(ax_pause, "Pause/Resume")
    btn_stop = Button(ax_stop, "Stop")

    btn_pause.on_clicked(toggle_pause)
    btn_stop.on_clicked(stop_execution)

def start_visualization(customers, depot):
    plt.ion()
    plot_routes(customers, depot, [])
    buttons()
    plt.show(block=False)

def close_plot():
    plt.ioff()
    plt.show()