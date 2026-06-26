import math
import os
import time
from collections import defaultdict
from omegaconf import DictConfig
from src.BAB_CBUS_21 import BAB
from src.DP_CBUS_21 import DP
from src.CP_CBUS_21 import CP
from src.ACO_CBUS_21 import ACO
from src.ALNS_CBUS_21 import ALNS_SA
from src.GA_CBUS_21 import GA
from src.GREEDY_CBUS_21 import GREEDY
from src.HC_CBUS_21 import HC
from src.SA_CBUS_21 import SA
from src.TS_CBUS_21 import TS

class Evaluator:
    def read_input(self, path, cfg: DictConfig):
        data = []
        with open(path, 'r') as f:
            for line in f:
                data.append(line.strip())
            
        n, k = map(int, data[0].split())
        c = []
        for i in range(2*n+1):
            c.append(list(map(int, data[i+1].split())))

        timelimit = cfg.timelimit

        return n,k,c,timelimit

    def calc_cost(self, c, route):
        ans = c[0][route[0]]
        for i in range(len(route)-1):
            ans += c[route[i]][route[i+1]]
        ans += c[route[-1]][0]
        return ans

    def evaluate(self, n, k, c, timelimit):
        methods = ["BAB", "DP", "CP", 'ACO', 'ALNS', 'GA', 'GREEDY', 'HC', 'SA', 'TS']

        print(f"[eval] evaluating methods on input size {n}")
        score = defaultdict(float)
        runtime = defaultdict(float)

        def evaluate_method(method, solver):
            start = time.time()
            _, route = solver.solve()
            end = time.time()

            if route == "TLE":
                score[method] = float("nan")
                runtime[method] = "TLE"
            elif not route:
                score[method] = float("nan")
                runtime[method] = f"{end - start:.4f}"
            else:
                score[method] = self.calc_cost(c, route)
                runtime[method] = f"{end - start:.4f}"

            print(f"    [{method.lower()}] score: {score[method]}")

        evaluate_method("BAB", BAB(n, k, c, timelimit))
        evaluate_method("DP", DP(n, k, c, timelimit))
        evaluate_method("CP", CP(n, k, c, timelimit))
        evaluate_method("ACO", ACO(n, k, c))
        evaluate_method("ALNS", ALNS_SA(n, k, c, timelimit=timelimit))
        evaluate_method("GA", GA(n, k, c, timelimit=timelimit))
        evaluate_method("GREEDY", GREEDY(n, k, c))
        evaluate_method("HC", HC(n, k, c))
        evaluate_method("SA", SA(n, k, c, timelimit=timelimit))
        evaluate_method("TS", TS(n, k, c))

        valid_scores = [
            score[method]
            for method in methods
            if math.isfinite(score[method])
        ]

        if not valid_scores:
            return n, score, runtime

        best = min(valid_scores)

        for method in methods:
            if not math.isfinite(score[method]):
                score[method] = float("nan")
                continue

            if best == 0:
                score[method] = 0.0 if score[method] == 0 else float("inf")
            else:
                gap = 100 * (score[method] - best) / best
                score[method] = round(gap, 4)

        return n, score, runtime
