# linkedlist_module.py

class Node:
    def __init__(self, trip):
        self.trip = trip
        self.next = None

class TripHistory:
    def __init__(self):
        self.head = None

    def add_trip(self, trip):
        # newest trip at head
        new_node = Node(trip)
        new_node.next = self.head
        self.head = new_node

    def get_history(self):
        trips = []
        current = self.head
        while current:
            trips.append(current.trip)
            current = current.next
        return trips  # newest -> oldest

    def get_reverse_history(self):
        return list(reversed(self.get_history()))

    def save_to_file(self, filename="trip_history.txt"):
        trips = self.get_history()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                for t in trips:
                    f.write(t + "\n")
        except Exception as e:
            raise e

    def load_from_file(self, filename="trip_history.txt"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            # clear current history and load preserving order in file (file assumed newest->oldest)
            self.head = None
            # file contains newest->oldest, so add in reverse to end up with same order in memory
            for line in reversed(lines):
                self.add_trip(line)
        except FileNotFoundError:
            # nothing to load
            return
