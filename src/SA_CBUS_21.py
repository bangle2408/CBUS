import sys,time,io,os
from collections import defaultdict
import random
import math

INF = 1<<60

class SA:
    def __init__(self, n, k, c, stop_temperture = 1e-4, iterations = 500000, alpha = 0.995, timelimit=290):
        self.n = n 
        self.k = k
        self.c = c
        self.Tmin = stop_temperture
        self.start_time = time.time()
        self.timelimit = timelimit
        self.iterations = iterations
        
        self.alpha = alpha

        self.cur_route, self.cur_cost = self.init_greedy_route()
        self.T = self.init_temperature(self.cur_route, self.cur_cost)
        self.best_route = self.cur_route[:]
        self.best_cost = self.cur_cost

    def solve(self):
        self.run()
        return self.n, self.best_route

    def get_neighbors(self, route):
        r = random.random()

        if r<=0.25:
            return self.pair_relocate(route)     
        elif r<=0.35:
            return self.pair_swap(route)         
        elif r<=0.75:
            return self.pickup_relocate(route)   

        return self.delivery_relocate(route) 

    def calc_prob(self, T, cost):
        if T <= 0: return 0.0
        delta = -(cost/T)
        # print(delta, math.exp(delta))
        if delta <= -650: return 0
        return math.exp(delta)

    def run(self):
        while self.iterations:
            self.end_time = time.time()
            if self.end_time - self.start_time >= self.timelimit:
                break
            new_route = self.get_neighbors(self.cur_route)
            new_cost = self.calc_cost(new_route)
            # print(new_cost)

            if new_cost - self.cur_cost <= 0 or random.random() <= self.calc_prob(self.T, new_cost - self.cur_cost):
            # if new_cost - self.cur_cost <= 0:
                self.cur_cost = new_cost
                self.cur_route = new_route[:]

            if self.cur_cost < self.best_cost:
                self.best_route = self.cur_route[:]
                self.best_cost = self.cur_cost
                
            self.T = min(self.T*self.alpha, self.Tmin)
            self.iterations -= 1

    def init_temperature(self, route, cost, samples = 20, p0 = 0.8):
        deltas = []
        for _ in range(samples):
            new_route = self.get_neighbors(route)
            new_cost = self.calc_cost(new_route)
            delta = new_cost - cost
            if delta > 0: deltas.append(delta)
        
        if not deltas: return 1

        avg = sum(deltas)/len(deltas)
        return -avg/math.log(p0)


    def is_valid(self, route):
        on = defaultdict(int)
        load = 0
        for i in route:
            if i <= self.n:
                on[i] += 1
                load += 1
            else:
                if not on[i-self.n]: return False
                load -= 1
            if load > self.k: return False

        return True

    def calc_cost(self, route):
        res = self.c[0][route[0]]
        for i in range(len(route)-1):
            res += self.c[route[i]][route[i+1]]
        res += self.c[route[-1]][0]
        return res

    def pair_relocate(self, route):
        while 1:
            pick = random.randint(1,self.n)
            deliv = pick + self.n
            
            base = [x for x in route if x!=pick and x!=deliv]
            L = len(base)


            p = random.randint(0, L)
            tmp = base[:p] + [pick] + base[p:]
            q = random.randint(p+1, L+1)
            new_route = tmp[:q] + [deliv] + tmp[q:]
            if self.is_valid(new_route):
                return new_route

    def pair_swap(self, route):
        while 1:
            new_route = route[:]
            a = random.randint(1,self.n)
            b = random.randint(1, self.n)
            if a == b: continue
            
            for idx, node in enumerate(route):
                if node == a:
                    new_route[idx] = b
                elif node == b:
                    new_route[idx] = a
                elif node == a+self.n:
                    new_route[idx] = b +self.n
                elif node == b+self.n:
                    new_route[idx] = a+self.n

            if self.is_valid(new_route): return new_route

    def pickup_relocate(self, route):
        while 1:
            pick = random.randint(1,self.n)
            base = []
            delivery = None
            for idx, node in enumerate(route):
                if node != pick:
                    base.append(node)
                if node == pick + self.n:
                    delivery = idx

            p = random.randint(0, delivery)
            new_route = base[:p] + [pick] + base[p:]

            if self.is_valid(new_route):
                return new_route

    def delivery_relocate(self, route):
        while 1:
            delivery = random.randint(1,self.n) + self.n
            base = []
            pick = None
            for idx, node in enumerate(route):
                if node != delivery:
                    base.append(node)
                if node == delivery - self.n:
                    pick = idx

            p = random.randint(pick+1, len(base))
            new_route = base[:p] + [delivery] + base[p:]

            if self.is_valid(new_route):
                return new_route

    def init_greedy_route(self):
        picked = [0 for _ in range(2*self.n+1)]
        load = 0
        last = 0
        path = []
        onbus = set()
        total_cost = 0

        while len(path) < 2*self.n:
            candidates = []

            if load < self.k:
                for i in range(1,self.n+1):
                    if not picked[i]:
                        candidates.append(i)

            for i in onbus:
                candidates.append(i+self.n)

            nxt = min(candidates, key = lambda x: self.c[last][x])

            total_cost += self.c[last][nxt]

            path.append(nxt)

            if nxt <= self.n:
                picked[nxt] = 1
                load += 1
                onbus.add(nxt)
            else:
                load -= 1
                onbus.remove(nxt-self.n)

            last = nxt

        total_cost += self.c[last][0]

        return path,total_cost

def solve():
    n,k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2*n+1)]
    n, best_route = SA(n,k,c).solve()
    print(n)
    print(*best_route)

def main():
    #Code
    t = 1
    for i in range(1,t+1):
        solve()

if __name__ == '__main__':
    main()
