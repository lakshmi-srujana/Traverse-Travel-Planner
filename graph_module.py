# graph_module.py
from collections import deque

class Graph:
    def __init__(self):
        self.graph = {}
        self.recommendations = {}  # explicit recommendations (hashmap)

    def add_city(self, city):
        if city not in self.graph:
            self.graph[city] = []

    def add_edge(self, city1, city2):
        self.add_city(city1)
        self.add_city(city2)
        if city2 not in self.graph[city1]:
            self.graph[city1].append(city2)
        if city1 not in self.graph[city2]:
            self.graph[city2].append(city1)

    def get_all_routes(self):
        routes = []
        for city in sorted(self.graph.keys()):
            connections = ", ".join(sorted(self.graph[city]))
            routes.append(f"{city} → {connections}")
        return "\n".join(routes) if routes else "No routes defined."

    def bfs(self, start, goal):
        if start not in self.graph or goal not in self.graph:
            return None
        visited = set()
        queue = deque([[start]])

        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == goal:
                return path
            if node not in visited:
                visited.add(node)
                for neighbor in self.graph.get(node, []):
                    if neighbor not in visited:
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append(new_path)
        return None

    def dfs(self, start, goal, visited=None, path=None):
        if start not in self.graph or goal not in self.graph:
            return None
        if visited is None:
            visited = set()
        if path is None:
            path = [start]
        visited.add(start)
        if start == goal:
            return path
        for neighbor in self.graph.get(start, []):
            if neighbor not in visited:
                res = self.dfs(neighbor, goal, visited, path + [neighbor])
                if res:
                    return res
        return None

    def add_recommendation(self, city, suggestion):
        if city not in self.recommendations:
            self.recommendations[city] = []
        if suggestion not in self.recommendations[city]:
            self.recommendations[city].append(suggestion)

    def get_recommendation(self, city, max_hops=2, max_results=5):
        """
        Return explicit recommendations if available; otherwise return nearby cities
        within max_hops using BFS (excluding the city itself).
        """
        if city in self.recommendations and self.recommendations[city]:
            return list(dict.fromkeys(self.recommendations[city]))  # preserve order, unique

        # fallback: BFS up to max_hops to find nearby cities
        if city not in self.graph:
            return []

        visited = set([city])
        queue = deque([(city, 0)])
        results = []
        while queue:
            node, depth = queue.popleft()
            if 0 < depth <= max_hops:
                if node not in results:
                    results.append(node)
            if depth < max_hops:
                for neigh in self.graph.get(node, []):
                    if neigh not in visited:
                        visited.add(neigh)
                        queue.append((neigh, depth + 1))
            if len(results) >= max_results:
                break
        return results[:max_results]
