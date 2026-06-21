import os
import time
from collections import defaultdict
from omegaconf import DictConfig
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
        print(f"[eval] evaluating methods on input size {n}")
        score = defaultdict(float)
        runtime = defaultdict(float)

        start = time.time()
        aco = ACO(n,k,c).solve()
        end = time.time()
        runtime['ACO'] = f"{end - start:.4f}"
        score['ACO'] = self.calc_cost(c, aco[1])
        print(f"    [aco] score: {score['ACO']}")

        start = time.time()
        alns = ALNS_SA(n,k,c,timelimit = timelimit).solve()
        end = time.time()
        runtime['ALNS'] = f"{end - start:.4f}"
        score['ALNS'] = self.calc_cost(c, alns[1])
        print(f"    [alns] score: {score['ALNS']}")

        start = time.time()
        ga = GA(n,k,c,timelimit = timelimit).solve()
        end = time.time()
        runtime['GA'] = f"{end - start:.4f}"
        score['GA'] = self.calc_cost(c, ga[1])
        print(f"    [ga] score: {score['GA']}")

        start = time.time()
        greedy = GREEDY(n,k,c).solve()
        end = time.time()
        runtime['GREEDY'] = f"{end - start:.4f}"
        score['GREEDY'] = self.calc_cost(c, greedy[1])
        print(f"    [greedy] score: {score['GREEDY']}")

        start = time.time()
        hc = HC(n,k,c).solve()
        end = time.time()
        runtime['HC'] = f"{end - start:.4f}"
        score['HC'] = self.calc_cost(c, hc[1])
        print(f"    [hc] score: {score['HC']}")

        start = time.time()
        sa = SA(n,k,c,timelimit = timelimit).solve()
        end = time.time()
        runtime['SA'] = f"{end - start:.4f}"
        score['SA'] = self.calc_cost(c, sa[1])
        print(f"    [sa] score: {score['SA']}")

        start = time.time()
        ts = TS(n,k,c).solve()
        end = time.time()
        runtime['TS'] = f"{end - start:.4f}"
        score['TS'] = self.calc_cost(c, ts[1])
        print(f"    [ts] score: {score['TS']}")

        return n, score, runtime

