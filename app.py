from flask import Flask, render_template, request, jsonify
from queue import Queue
import heapq
import json, os

app = Flask(__name__)

# --------------------------
# 🧩 Data Structures Section
# --------------------------

class RouteNode:
    def __init__(self, start, goal, path, cost=None):
        self.start = start
        self.goal = goal
        self.path = path
        self.cost = cost
        self.next = None

class RouteHistory:
    def __init__(self):
        self.head = None

    def add_route(self, start, goal, path, cost=None):
        new_node = RouteNode(start, goal, path, cost)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_all_routes(self):
        routes = []
        current = self.head
        while current:
            routes.append({
                "start": current.start,
                "goal": current.goal,
                "path": current.path,
                "cost": current.cost
            })
            current = current.next
        return routes


# ✅ Make Undirected Graph
def make_undirected(graph):
    undirected = {}
    for city, neighbors in graph.items():
        if city not in undirected:
            undirected[city] = set()
        for neighbor in neighbors:
            undirected[city].add(neighbor)
            undirected.setdefault(neighbor, set()).add(city)
    return {city: list(neigh) for city, neigh in undirected.items()}


# ✅ Save/Load graph
def save_graph_to_file():
    os.makedirs("history", exist_ok=True)
    with open("history/graph.json", "w") as f:
        json.dump(graph, f, indent=4)

def load_graph_from_file():
    if os.path.exists("history/graph.json"):
        with open("history/graph.json", "r") as f:
            return json.load(f)
    return None


# -----------------------------
# Graph Initialization
# -----------------------------
default_graph = {
    "Mumbai": ["Delhi", "Bangkok"],
    "Delhi": ["Tokyo", "Kyoto"],
    "Tokyo": ["Osaka"],
    "Bangkok": ["Osaka", "Singapore"],
    "Osaka": [],
    "Singapore": [],
    "Kyoto": [],
    "Hyderabad": ["Delhi"]
}

graph = load_graph_from_file() or make_undirected(default_graph)

costs = {
    ("Mumbai", "Delhi"): 3,
    ("Delhi", "Tokyo"): 4,
    ("Tokyo", "Osaka"): 2,
    ("Bangkok", "Singapore"): 1,
    ("Bangkok", "Osaka"): 3,
    ("Delhi", "Kyoto"): 5,
}
for (a, b), c in list(costs.items()):
    costs[(b, a)] = c

recent_searches = []  # Stack
visited_queue = Queue()  # Queue
route_history = RouteHistory()  # Linked List
trip_plan = []


# -----------------------------
# ✅ Helper Functions (Fixed)
# -----------------------------

def dfs_all_paths(start, goal, path=None):
    if path is None:
        path = [start]
    if start == goal:
        return [path]
    if start not in graph:
        return []
    paths = []
    for neighbor_info in graph[start]:
        # ✅ FIXED HERE: Handle tuple like (city, cost)
        neighbor = neighbor_info[0] if isinstance(neighbor_info, (list, tuple)) else neighbor_info
        if neighbor not in path:
            new_paths = dfs_all_paths(neighbor, goal, path + [neighbor])
            paths.extend(new_paths)
    return paths


def bfs_shortest_path(start, goal):
    visited = set()
    queue = [[start]]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            for neighbor_info in graph.get(node, []):
                # ✅ FIXED HERE
                neighbor = neighbor_info[0] if isinstance(neighbor_info, (list, tuple)) else neighbor_info
                queue.append(path + [neighbor])
            visited.add(node)
    return None


def best_route_by_cost(start, goal):
    heap = [(0, start, [start])]
    visited = set()
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == goal:
            return cost, path
        if node in visited:
            continue
        visited.add(node)
        for neighbor_info in graph.get(node, []):
            # ✅ FIXED HERE
            if isinstance(neighbor_info, (list, tuple)):
                next_city, edge_cost = neighbor_info[0], neighbor_info[1]
            else:
                next_city, edge_cost = neighbor_info, costs.get((node, neighbor_info), 10)
            heapq.heappush(heap, (cost + edge_cost, next_city, path + [next_city]))
    return None, []


def has_cycle_util(city, visited, parent):
    visited.add(city)
    for neighbor_info in graph.get(city, []):
        # ✅ FIXED HERE
        neighbor = neighbor_info[0] if isinstance(neighbor_info, (list, tuple)) else neighbor_info
        if neighbor not in visited:
            if has_cycle_util(neighbor, visited, city):
                return True
        elif parent != neighbor:
            return True
    return False


# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/explore_paths", methods=["POST"])
def explore_paths():
    data = request.get_json()
    start, goal = data.get("start", "").title(), data.get("goal", "").title()
    recent_searches.append((start, goal))
    if len(recent_searches) > 5:
        recent_searches.pop(0)
    paths = dfs_all_paths(start, goal)
    if paths:
        route_history.add_route(start, goal, paths[0])
        return jsonify({"paths": paths})
    return jsonify({"error": "No possible paths found"})


@app.route("/shortest_path", methods=["POST"])
def shortest_path():
    data = request.get_json()
    start, goal = data.get("start", "").title(), data.get("goal", "").title()
    visited_queue.put(start)
    path = bfs_shortest_path(start, goal)
    if path:
        route_history.add_route(start, goal, path)
        return jsonify({"path": path})
    return jsonify({"error": "No route found"})


@app.route("/add_city", methods=["POST"])
def add_city():
    data = request.get_json()
    city = data.get("city", "").title()
    if not city:
        return jsonify({"error": "City name required!"})
    if city in graph:
        return jsonify({"error": f"{city} already exists in the network!"})
    graph[city] = []
    save_graph_to_file()
    return jsonify({"message": f"🏙️ City '{city}' added successfully!", "graph": graph})


@app.route("/add_route", methods=["POST"])
def add_route():
    data = request.get_json()
    city1 = data.get("city1")
    city2 = data.get("city2")
    cost = int(data.get("cost", 1))
    if not city1 or not city2:
        return jsonify({"error": "Both cities are required!"})
    if city1 not in graph:
        graph[city1] = []
    if city2 not in graph:
        graph[city2] = []
    # ✅ store tuples properly
    graph[city1].append((city2, cost))
    graph[city2].append((city1, cost))
    save_graph_to_file()
    return jsonify({"message": f"✅ Route added between {city1} and {city2} (Cost: {cost})"})


@app.route("/delete_route", methods=["POST"])
def delete_route():
    data = request.get_json()
    city1 = data.get("city1", "").title()
    city2 = data.get("city2", "").title()
    if city1 not in graph or city2 not in graph:
        return jsonify({"error": "One or both cities not found!"})
    # ✅ handle tuple format
    graph[city1] = [n for n in graph[city1] if not (isinstance(n, (list, tuple)) and n[0] == city2) and n != city2]
    graph[city2] = [n for n in graph[city2] if not (isinstance(n, (list, tuple)) and n[0] == city1) and n != city1]
    save_graph_to_file()
    return jsonify({"message": f"🗑️ Route between {city1} and {city2} deleted!"})


@app.route("/save_graph", methods=["POST"])
def save_graph():
    save_graph_to_file()
    return jsonify({"message": "💾 Graph saved successfully!"})


@app.route("/load_graph", methods=["GET"])
def load_graph():
    global graph
    loaded = load_graph_from_file()
    if not loaded:
        return jsonify({"error": "No saved graph found!"})
    graph = loaded
    return jsonify({"message": "📂 Graph loaded successfully!", "graph": graph})


@app.route("/best_route", methods=["POST"])
def best_route():
    data = request.get_json()
    start, goal = data.get("start", "").title(), data.get("goal", "").title()
    cost, path = best_route_by_cost(start, goal)
    if path:
        route_history.add_route(start, goal, path, cost)
        return jsonify({"path": path, "cost": cost})
    return jsonify({"error": "No best route found"})


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    city = data.get("city", "").title()
    if city not in graph:
        return jsonify({"error": f"{city} not found in the travel network!"})
    rec = [n[0] if isinstance(n, (list, tuple)) else n for n in graph.get(city, [])]
    if not rec:
        return jsonify({"error": f"No direct routes found from {city}."})
    return jsonify({"recommendations": rec})


@app.route("/most_connected")
def most_connected():
    if not graph:
        return jsonify({"error": "Graph is empty!"})
    most_city = max(graph, key=lambda k: len(graph[k]))
    return jsonify({"city": most_city, "connections": len(graph[most_city])})


@app.route("/has_cycle")
def has_cycle():
    visited = set()
    for city in graph:
        if city not in visited:
            if has_cycle_util(city, visited, None):
                return jsonify({"cycle": True})
    return jsonify({"cycle": False})


@app.route("/add_to_plan", methods=["POST"])
def add_to_plan():
    data = request.get_json()
    city = data.get("city", "").title()
    if not city:
        return jsonify({"error": "City name required!"})
    trip_plan.append(city)
    return jsonify({"message": f"{city} added to trip plan!"})


@app.route("/view_plan")
def view_plan():
    if not trip_plan:
        return jsonify({"plan": [], "message": "Trip plan is empty!"})
    return jsonify({"plan": trip_plan})


@app.route("/search_city", methods=["POST"])
def search_city():
    data = request.get_json()
    prefix = data.get("prefix", "").title()
    if not prefix:
        return jsonify({"error": "Please enter a prefix!"})
    matches = [city for city in graph.keys() if city.startswith(prefix)]
    if matches:
        return jsonify({"matches": matches})
    else:
        return jsonify({"message": "No cities found starting with that prefix."})


@app.route("/recent")
def recent():
    return jsonify({"recent": recent_searches})


@app.route("/visited")
def visited():
    return jsonify({"visited": list(visited_queue.queue)})


@app.route("/history")
def history():
    routes = route_history.get_all_routes()
    return jsonify({"history": routes})


# -----------------------------
# Run Flask App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
