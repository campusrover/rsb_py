import redis
import json
import cProfile


class RedisUtil(object):
    def __init__(self, ns, keys={"Map": "list", "Odom": "string", "Lidar": "string"}, server=True):
        self.ns = ns                     # user namespace
        self.last_id = 0                 # 
        self.keys = set(keys.keys())     # set of keys that this redis interface cares about
        self.key_types = keys            # dict mapping keys to their redis data type, e.g. string, list, etc
        if server:
            self.redishandle = redis.Redis(
                host="redis-10221.c10.us-east-1-3.ec2.cloud.redislabs.com",
                port=10221,
                password="ROSlab134"
            )
        else:
            self.redishandle = redis.Redis()
        for k in self.keys:
            self.__setattr__(k.lower(), None)    # create attributes for each key in this object

    def nskey(self, keyname):
        """
        namespaces a key
        """
        if self.ns:
            return self.ns + "/" + keyname
        else:
            return keyname

    def my_keys(self):
        """
        Returns a list of namespaced keys that this redisutil currently pays attention to
        """
        return sorted([self.nskey(key) for key in self.keys])

    def add_key(self, keyname, keytype):
        """
        adds a new key to retrieve. creates self.keyname attribute (lowercase, so key "Data" becomse self.data)
        """
        if keyname not in self.keys:
            self.keys.add(keyname)
            self.key_types[keyname] = keytype
            self.__setattr__(keyname.lower(), None)
            return True
        else:
            return False

    def remove_key(self, keyname):
        """
        removes key from list of keys. deletes self.keyname attribute
        """
        if keyname in self.keys:
            self.keys.remove(keyname)
            self.key_types.pop(keyname)
            self.__delattr__(keyname.lower())
            return True
        else:
            return False 

    def assert_key_types(self):
        """
        makes sure that the given key types match the types in redis

        Returns that number of keys that had mismatched types
        """
        adjustments = 0
        for k in self.keys:
            if self.redishandle.exists(self.nskey(k)) and self.redishandle.type(self.nskey(k)) != self.key_types[k]:
                self.key_types[k] = self.redishandle.type(self.nskey(k))
                adjustments += 1
        return adjustments

    def clients(self):
        """
        returns a list of namespaces in the redis server
        """
        namespaced_keys = self.redishandle.keys("*/*")
        clients = set([key.decode("UTF-8").split("/")[0] for key in namespaced_keys])
        return sorted(list(clients))

    def rsb_all_keys(self, clients):
        rsb_all_keys = list(map(lambda x: self.redishandle.keys(x + "/*"), clients))
        return rsb_all_keys

    def preview_maps(self, low=0, high=-1):
        raw_bytes = self.redishandle.lrange(self.nskey("Map"), low, high)
        rez = list(map(lambda x: json.loads(str(x.decode("utf8"))), raw_bytes))
        return rez

    def get_next_map(self):
        while True:
            # self.redishandle.ltrim(self.ns + "/Map", -10, -1)
            raw_bytes = self.redishandle.lindex(self.nskey("/Map"), -1)
            if not raw_bytes:
                return None
            rez = json.loads(str(raw_bytes.decode("utf8")))
            if rez["id"] >= self.last_id:
                break
            #print(f"dumping {rez['id']}")
            self.last_id = rez["id"]
        self.last_id = rez["id"]
        return rez

    def reset(self):
        """
        requests that Robot_Services perform a reset
        """
        self.redishandle.set(self.nskey("Bridge_Reset"), 1)
        self.last_id = 0

    def get_robot_info(self):
        res = {"odom": None, "lidar": None}
        raw_bytes = self.redishandle.get(self.ns + "/Odom")
        if raw_bytes:
            res["odom"] = json.loads(str(raw_bytes.decode("utf8")))
        raw_bytes = self.redishandle.get(self.ns + "/Lidar")
        if raw_bytes:
            res["lidar"] = json.loads(str(raw_bytes.decode("utf8")))
        return res
    
    def bulk_update(self):
        """
        updates all fields in self.keys at once
        """
        key_list = list(self.keys)
        pipe = self.redishandle.pipeline()
        for k in key_list:
            if self.key_types[k] == "string":
                pipe.get(self.nskey(k))
            elif self.key_types[k] == "list":
                pipe.lindex(self.nskey(k), -1)
            else:
                pipe.get("#Fake_$Key")  # pads the list returned by pipe.execute if a key can't be fetched
        result = [itm.decode("utf8") if itm else "" for itm in pipe.execute()]
        [self.__setattr__(key.lower(), json.loads(str(itm))) if itm else self.__setattr__(key.lower(), None) for itm, key in zip(result, key_list)]

if __name__ == "__main__":
    def to_profile():
        oldid = 0
        for i in range(50):
            m = r.get_next_map()
            for i in range(5):
                id = r.get_robot_info()["odom"]["time"]
                if id != oldid:
                    break
            if oldid != id:
                print(id)
            oldid = id
    r = RedisUtil("pito1")
    #cProfile.run('to_profile()', sort=2)
    r.bulk_update()
    print(r.odom, r.map, r.lidar)

