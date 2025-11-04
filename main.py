# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from data import create_graph, create_tree, get_all_cities
from linkedlist_module import TripHistory

graph = create_graph()
tree = create_tree()
history = TripHistory()
cities = get_all_cities()
trip_plan = []      # Array/List for planner
recent_stack = []   # Stack for most recent destinations (push on visit)

# Load existing history from file (if any)
history.load_from_file()

def refresh_comboboxes():
    # keep combobox choices in sync with cities list
    start_city["values"] = sorted(cities)
    end_city["values"] = sorted(cities)

def find_route(method):
    start = start_city.get()
    end = end_city.get()
    if not start or not end:
        messagebox.showwarning("Input Error", "Select both start and end cities.")
        return
    if start == end:
        output.set(start)
        return

    if method == "BFS":
        path = graph.bfs(start, end)
    else:
        path = graph.dfs(start, end)

    if path:
        text = " → ".join(path)
        output.set(text)
        history.add_trip(f"{method}: {text}")
        recent_stack.append(end)
    else:
        output.set("No path found")

def shortest_path():
    start = start_city.get()
    end = end_city.get()
    if not start or not end:
        messagebox.showwarning("Input Error", "Select both cities.")
        return
    path = graph.bfs(start, end)
    if path:
        messagebox.showinfo("Shortest Path", " → ".join(path))
    else:
        messagebox.showwarning("No path", "No path found between these cities.")

def show_history():
    trips = history.get_history()
    if not trips:
        messagebox.showinfo("Trip History", "No trips yet.")
    else:
        # show newest first
        messagebox.showinfo("Trip History", "\n".join(trips))

def show_tree():
    import io, sys
    buffer = io.StringIO()
    old = sys.stdout
    sys.stdout = buffer
    tree.display()
    sys.stdout = old
    messagebox.showinfo("Destination Hierarchy", buffer.getvalue())

def add_city():
    new_city = simpledialog.askstring("Add City", "Enter new city name:")
    if new_city:
        new_city = new_city.strip()
        if not new_city:
            return
        if new_city in cities:
            messagebox.showinfo("Info", f"{new_city} already exists.")
            return
        cities.append(new_city)
        graph.add_city(new_city)
        refresh_comboboxes()
        messagebox.showinfo("Success", f"City '{new_city}' added.")

def add_route():
    city1 = simpledialog.askstring("Add Route", "From city:")
    if city1 is None: return
    city2 = simpledialog.askstring("Add Route", "To city:")
    if city2 is None: return
    city1 = city1.strip(); city2 = city2.strip()
    if not city1 or not city2:
        return
    graph.add_edge(city1, city2)
    for c in (city1, city2):
        if c not in cities:
            cities.append(c)
    refresh_comboboxes()
    messagebox.showinfo("Success", f"Route added: {city1} ↔ {city2}")

def view_routes():
    routes = graph.get_all_routes()
    messagebox.showinfo("All Routes", routes)

def add_to_trip_plan():
    city = simpledialog.askstring("Trip Planner", "Enter city to add to plan:")
    if city:
        city = city.strip()
        if city:
            trip_plan.append(city)
            messagebox.showinfo("Planner", f"{city} added to your trip plan.")

def view_trip_plan():
    if not trip_plan:
        messagebox.showinfo("Planner", "Trip plan is empty.")
    else:
        messagebox.showinfo("Planner", " → ".join(trip_plan))

def search_city():
    city = simpledialog.askstring("Search City", "Enter city name to search:")
    if city:
        city = city.strip()
        if city in cities:
            messagebox.showinfo("Search Result", f"{city} is available.")
        else:
            messagebox.showwarning("Search Result", f"{city} not found.")

def show_recent():
    if not recent_stack:
        messagebox.showinfo("Recent Cities", "No recent visits yet.")
    else:
        # show last 5 most recent
        last5 = list(reversed(recent_stack[-5:]))
        messagebox.showinfo("Recent Cities (most recent first)", " → ".join(last5))

def add_to_tree():
    parent = simpledialog.askstring("Add to Hierarchy", "Enter parent (e.g., India):")
    if parent is None: return
    new_place = simpledialog.askstring("Add to Hierarchy", "Enter new city/country to add:")
    if new_place is None: return
    if tree.add_location(parent.strip(), new_place.strip()):
        messagebox.showinfo("Added", f"{new_place} added under {parent}.")
    else:
        messagebox.showwarning("Error", "Parent node not found in hierarchy.")

def recommend_city():
    base = simpledialog.askstring("Recommend", "Enter a city to get recommendations:")
    if not base:
        return
    recs = graph.get_recommendation(base.strip(), max_hops=2, max_results=6)
    if recs:
        messagebox.showinfo("Recommendations", f"From {base.strip()}, try: {', '.join(recs)}")
    else:
        messagebox.showinfo("Recommendations", "No recommendations available for this city.")

def save_history():
    try:
        history.save_to_file()
        messagebox.showinfo("Saved", "Trip history saved to 'trip_history.txt'.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save history: {e}")

# GUI
root = tk.Tk()
root.title("🌍 Traverse 3.0 - Smart Travel Planner")
root.geometry("700x750")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Select Starting City:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
start_city = ttk.Combobox(frame, values=sorted(cities), width=40)
start_city.grid(row=0, column=1, padx=8, pady=4)

tk.Label(frame, text="Select Destination City:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
end_city = ttk.Combobox(frame, values=sorted(cities), width=40)
end_city.grid(row=1, column=1, padx=8, pady=4)

output = tk.StringVar()
tk.Label(root, textvariable=output, wraplength=650, fg="blue").pack(pady=8)

# Buttons grouped
button_frame = tk.Frame(root)
button_frame.pack(pady=6)

btns = [
    ("Find Route (BFS)", lambda: find_route("BFS")),
    ("Find Route (DFS)", lambda: find_route("DFS")),
    ("Shortest Path", shortest_path),
    ("View All Routes", view_routes),
    ("Add City", add_city),
    ("Add Route", add_route),
    ("Search City", search_city),
    ("Show Trip History", show_history),
    ("Save Trip History", save_history),
    ("Show Destination Tree", show_tree),
    ("Add to Hierarchy Tree", add_to_tree),
    ("Add to Trip Planner", add_to_trip_plan),
    ("View Trip Planner", view_trip_plan),
    ("Recent Cities (Stack)", show_recent),
    ("City Recommendations", recommend_city)
]

# place buttons in a grid
r = 0; c = 0
for (label, cmd) in btns:
    b = tk.Button(button_frame, text=label, width=25, command=cmd)
    b.grid(row=r, column=c, padx=6, pady=6)
    c += 1
    if c > 1:
        c = 0
        r += 1

refresh_comboboxes()
root.mainloop()
