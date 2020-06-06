import json

class World(object):
    def __init__(self, size={"width": 100, "height": 100}):
        self.size = size
        self.walls = []

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append((x1, y1, x2, y2))

    def wall_count(self):
        return len(self.walls)

    def rebuild(self, json_state):
        if not json_state:
            self.walls = []
            self.size = {}
        else:
            self.size = {"width": json_state["width"], "height": json_state["height"]}
            self.walls = []
            for l in json_state["data"]:
                self.walls.append(l)
            self.id = json_state["id"]

    def __repr__(self):
        return f"World: walls: {self.wall_count()}, id: {self.id}"
