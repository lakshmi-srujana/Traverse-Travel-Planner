# tree_module.py

class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def display(self, level=0):
        print("  " * level + f"- {self.name}")
        for child in self.children:
            child.display(level + 1)

    def add_location(self, parent_name, new_place):
        if self.name == parent_name:
            self.children.append(TreeNode(new_place))
            return True
        for child in self.children:
            if child.add_location(parent_name, new_place):
                return True
        return False

    def search(self, name):
        if self.name == name:
            return True
        for child in self.children:
            if child.search(name):
                return True
        return False
