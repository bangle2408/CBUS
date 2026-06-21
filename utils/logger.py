import os
import json

class Logger:
    def __init__(self, log_dir, name = "log.jsonl"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, name)
        print(f"[INFO] [Logger] Logging to: {self.log_path}")

    def log(self, size, cap, scores, runtime):
        record = {
            "size": size,
            "capacity": cap,
            "Greedy": (scores["GREEDY"], runtime["GREEDY"]),
            "HC": (scores["HC"], runtime["HC"]),
            "ACO": (scores["ACO"], runtime["ACO"]),
            "TS": (scores["TS"], runtime["TS"]),
            "ALNS": (scores["ALNS"], runtime["ALNS"]),
            "SA": (scores["SA"], runtime["SA"]),
            "GA": (scores["GA"], runtime["GA"]),
        }

        with open(self.log_path, 'a') as f:
            f.write(json.dumps(record) + "\n")