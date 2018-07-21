import json
import socket
import time
import ping3


class GpuStats:
    number = 0
    hashrate = 0.0
    temp = 0
    fan = 0


class Stats:
    ping = None
    online = False
    version = ""
    runtime = 0
    hashrate = 0
    shares = 0
    rej_shares = 0
    pool = ""
    invalid_shares = 0
    pool_switches = 0
    gpus = []
    gpus_online = 0
    gpus_offline = 0
    max_temp = 0
    error = None

    def __init__(self, miner):
        self.miner = miner


class Miner:
    def __init__(self, host="127.0.0.1", port=3333, password=None):
        self.host = host
        self.port = port
        self.password = password

    def ping(self, timeout=1):
        try:
            res = ping3.ping(self.host, timeout)
            return int(res / 1000.0)
        except:
            return None


class Claymore(Miner):
    def execute_method(self, method, responds=True, params=None):
        request = {"id": 0, "jsonrpc": "2.0", "method": method}
        if params:
            request["params"] = params
        if self.password:
            request["psw"] = self.password

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((self.host, self.port))
            s.sendall("{}\n".format(json.dumps(request)).encode())
            if responds:
                res = s.recv(1024)
                if res != b"":
                    return json.loads(res.decode())["result"]
                else:
                    raise Exception("Unexpected empty response")

    def get_stats(self):
        s = Stats(self)
        s.ping = s.miner.ping()
        try:
            res = self.execute_method("miner_getstat1")
        except socket.timeout as ex:
            res = None
            s.error = "Network timeout"
        except Exception as ex:
            res = None
            s.error = str(ex)
        if not res:
            s.max_temp = None
            s.hashrate = None
            return s
        s.online = True
        s.version = res[0]
        s.runtime = int(res[1])
        s.pool = res[7]
        totals = res[2].split(";")
        s.hashrate = int(totals[0]) / 1000.0
        s.shares = int(totals[1])
        s.rej_shares = int(totals[2])

        details = res[8].split(";")
        s.invalid_shares = int(details[0])
        s.pool_switches = int(details[1])

        gpus = []
        hashrates = res[3].split(";")
        for g in hashrates:
            gs = GpuStats()
            gs.number = len(gpus)
            gs.hashrate = int(g) / 1000.0 if g != "off" else 0
            if gs.hashrate > 0:
                s.gpus_online += 1
            else:
                s.gpus_offline += 1
            gpus.append(gs)

        temps = res[6].split(";")
        for x in range(len(gpus)):
            gpus[x].temp = int(temps[x * 2])
            gpus[x].fan = int(temps[x * 2 + 1])
            if gpus[x].temp > s.max_temp:
                s.max_temp = gpus[x].temp

        s.gpus = gpus
        return s

    def print_stats(self):
        stats = self.get_stats()
        print(
            "Host: {}:{} ({}) | Up {} min".format(
                self.host, self.port, stats.version, stats.runtime
            )
        )
        print("Pool: {} ({} switches)".format(stats.pool, stats.pool_switches))
        print("Total hashrate: {} MH/s".format(stats.hashrate))
        print(
            "Shares: {} | Rejected: {} | Invalid: {}".format(
                stats.shares, stats.rej_shares, stats.invalid_shares
            )
        )
        for i in range(len(stats.gpus)):
            g = stats.gpus[i]
            print(
                "GPU #{}: {}MH/s | Temp: {}C | Fan: {}%".format(
                    i, g.hashrate, g.temp, g.fan
                )
            )

    def restart(self):
        self.execute_method("miner_restart", responds=False)

    def reboot(self):
        self.execute_method("miner_reboot", responds=False)
