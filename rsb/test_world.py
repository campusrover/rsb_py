from rsb import world


class TestMap:
    def setup(self):
        self.map_json = {
            "line_count": 2,
            "width": 19.2,
            "data": [[-3.1, -0.2, -1.6, -1.7], [-2.3, -1.3, -1.4, -1.9]],
            "id": 7,
            "height": 19.2,
        }

    def test_new_map(self):
        a = world.World({"width": 100, "height": 100})
        assert a.size["width"] == 100 and a.size["height"] == 100

    def test_json_reset(self):
        a = world.World({"width": 100, "height": 100})
        a.rebuild(self.map_json)
        assert (
            a.size["height"] == 19.2 and a.size["width"] == 19.2 and a.wall_count() == 2
        )
        assert a.walls[0] == [-3.1, -0.2, -1.6, -1.7]
