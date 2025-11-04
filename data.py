# data.py
from graph_module import Graph
from tree_module import TreeNode

def create_graph():
    g = Graph()

    # India cluster
    g.add_edge("Mumbai", "Delhi")
    g.add_edge("Delhi", "Agra")
    g.add_edge("Agra", "Jaipur")
    g.add_edge("Mumbai", "Hyderabad")
    g.add_edge("Hyderabad", "Bangalore")
    g.add_edge("Bangalore", "Chennai")
    g.add_edge("Mumbai", "Goa")
    g.add_edge("Goa", "Bangalore")

    # Japan cluster
    g.add_edge("Tokyo", "Osaka")
    g.add_edge("Osaka", "Kyoto")
    g.add_edge("Tokyo", "Kyoto")

    # Connect clusters (international/airport hubs)
    # Connect Delhi <-> Tokyo (flight route) so Mumbai -> ... -> Tokyo is reachable
    g.add_edge("Delhi", "Tokyo")    # hub connection (simulates international flight)
    # Optionally connect Hyderabad -> Tokyo too if wanted
    g.add_edge("Hyderabad", "Tokyo")

    # Recommendations (explicit)
    g.add_recommendation("Delhi", "Agra")
    g.add_recommendation("Goa", "Mumbai")
    g.add_recommendation("Tokyo", "Kyoto")
    g.add_recommendation("Mumbai", "Goa")

    return g

def create_tree():
    root = TreeNode("World")
    india = TreeNode("India")
    japan = TreeNode("Japan")

    india.add_child(TreeNode("Delhi"))
    india.add_child(TreeNode("Mumbai"))
    india.add_child(TreeNode("Goa"))
    india.add_child(TreeNode("Hyderabad"))
    india.add_child(TreeNode("Bangalore"))

    japan.add_child(TreeNode("Tokyo"))
    japan.add_child(TreeNode("Kyoto"))
    japan.add_child(TreeNode("Osaka"))

    root.add_child(india)
    root.add_child(japan)
    return root

def get_all_cities():
    return ["Mumbai", "Delhi", "Agra", "Jaipur", "Hyderabad", "Bangalore",
            "Chennai", "Goa", "Tokyo", "Osaka", "Kyoto"]
