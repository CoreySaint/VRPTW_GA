import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import threading

# Threading events for pause/stop buttons
is_paused = threading.Event()
is_paused.clear()
should_stop = threading.Event()
should_stop.clear()

# Helper function
def clear_previous_plot():
    plt.clf()

def plot_routes(customers, depot, routes, generation=None, best_distance=None):
    """
    Function to plot all the calculated routes within the current search space.
    Allows for dynamic updating of the GUI
    """
    # Clear current plot and plot starting nodes and depot
    clear_previous_plot()
    
    plt.scatter([depot[0]], [depot[1]], c='red', marker='s', label='Depot', s=100)
    plt.scatter(customers['x'], customers['y'], c='blue', label='Customers')

    colors = plt.cm.get_cmap('tab10', len(routes))

    # Iterate over the routes and plot said routes
    for i, route in enumerate(routes):
        route_x = [depot[0]] + [customers.iloc[c]['x'] for c in route] + [depot[0]]
        route_y = [depot[1]] + [customers.iloc[c]['y'] for c in route] + [depot[1]]
        plt.plot(route_x, route_y, color=colors(i), linewidth=2, label=f'Vehicle {i+1}')

    # Plot formatting
    plt.title(f"Generation {generation + 1} | Best Distance: {best_distance:.2f}" if generation else "Initial Routes")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(loc='upper right')
    plt.pause(0.1)

def toggle_pause(event):
    """
    Helper function to pause the current run of GA
    """
    # Logic to allow for proper button usage
    if is_paused.is_set():
        is_paused.clear()
        print("Resumed")
    else:
        is_paused.set()
        print("Paused")

def stop_execution(event):
    """
    Helper function to halt the current run of GA
    """
    should_stop.set()
    print("Stopped")

def buttons():
    """
    Adds Stop and Pause/Resume buttons to GUI window
    """
    # Location of the button in the GUI
    ax_pause = plt.axes([0.7, 0.02, 0.1, 0.05])
    ax_stop = plt.axes([0.82, 0.02, 0.1, 0.05])

    # Add the buttons
    btn_pause = Button(ax_pause, "Pause/Resume")
    btn_stop = Button(ax_stop, "Stop")

    # Allow for stoppage and pausing
    btn_pause.on_clicked(toggle_pause)
    btn_stop.on_clicked(stop_execution)

def start_visualization(customers, depot):
    """
    Main function to run helper functions and dynamically visualize GA
    """
    # Turn on visualization
    plt.ion()
    # Plot the routes
    plot_routes(customers, depot, [])
    # Add the buttons
    buttons()
    # Show the plot
    plt.show(block=False)

def close_plot():
    """
    Helper function to close the current plot
    """
    # Turn off plot
    plt.ioff()
    # Update plot
    plt.show()
