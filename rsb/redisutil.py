import redis
import json

class RedisUtil(object):
    def __init__(self, ns):
        self.ns = ns
        self.last_id = 0
        self.redishandle = redis.Redis(
            host="redis-10221.c10.us-east-1-3.ec2.cloud.redislabs.com",
            port=10221,
            password="ROSlab134"
        )

    def clients(self):
        map_keys = self.redishandle.keys("*/Map")
        clients = list(map(lambda x: x.decode("utf-8").replace("/Map", ""), map_keys))
        return clients

    def rsb_all_keys(self, clients):
        rsb_all_keys = list(map(lambda x: self.redishandle.keys(x + "/*"), clients))
        return rsb_all_keys

    def preview_maps(self, low=0, high=-1):
        raw_bytes = self.redishandle.lrange(self.ns + "/Map", low, high)
        rez = list(map(lambda x: json.loads(str(x.decode("utf8"))), raw_bytes))
        return rez

    def get_next_map(self):
        while True:
            # self.redishandle.ltrim(self.ns + "/Map", -10, -1)
            raw_bytes = self.redishandle.lrange(self.ns + "/Map", -1, -1)
            rez = json.loads(str(raw_bytes[0].decode("utf8")))
            if rez["id"] >= self.last_id:
                break
            print(f"dumping {rez['id']}")
            self.last_id = rez["id"]
        self.last_id = rez["id"]
        return rez

    def reset(self):
        self.redishandle.set(self.ns + "Bridge_Reset")
        self.last_id = 0

    def get_robot_info(self):
        raw_bytes = self.redishandle.get(self.ns + "/Odom")
        rez = json.loads(str(raw_bytes.decode("utf8")))
        return rez
        