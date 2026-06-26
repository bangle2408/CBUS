import sys,time,io,os
import random

INF = 1<<60

class GA:
    def __init__(self, n, k, c, generations = 50000, timelimit = 290):
        self.n = n
        self.k = k
        self.c = c
        self.settings()
        self.start_time = time.time()
        self.timelimit = timelimit
        self.generations = generations

        self.best_route = None
        self.best_cost = INF

        self.population = self.init_population()

    def solve(self):
        self.run()
        return self.n, self.best_route

    def settings(self):
        if self.n <= 10:
            self.pop_size = 160
            self.elite_size = 8
            self.tournament_size = 3
            self.crossover_rate = 0.95
            self.mutation_rate = 0.45

        elif self.n <= 100:
            self.pop_size = 120
            self.elite_size = 8
            self.tournament_size = 4
            self.crossover_rate = 0.90
            self.mutation_rate = 0.45

        elif self.n <= 500:
            self.pop_size = 75
            self.elite_size = 5
            self.tournament_size = 3
            self.crossover_rate = 0.70
            self.mutation_rate = 0.65

        elif self.n <= 1000:
            self.pop_size = 40
            self.elite_size = 3
            self.tournament_size = 2
            self.crossover_rate = 0.60
            self.mutation_rate = 0.75

        else:
            self.pop_size = 24
            self.elite_size = 2
            self.tournament_size = 2
            self.crossover_rate = 0.55
            self.mutation_rate = 0.90

    def select(self, scored):
        best_cost, best_route = random.choice(scored)

        for _ in range(self.tournament_size-1):
            cost, route = random.choice(scored)

            if cost < best_cost:
                best_cost = cost
                best_route = route

        return best_route

    def init_population(self):
        population = []

        greedy_route, greedy_cost = self.init_greedy_route()
        population.append(greedy_route)
        self.best_route = greedy_route[:]
        self.best_cost = greedy_cost

        greedy_variants = self.pop_size//3
        for _ in range(greedy_variants):
            route = greedy_route[:]
            mutation_times = random.randint(1,5)

            for _ in range(mutation_times):
                route = self.mutate(route)

            population.append(route)

        while len(population)<self.pop_size:
            population.append(self.random_route())

        return population

    def mutate(self, route):
        r = random.random()

        if r < 0.30: return self.pair_relocate(route)
        elif r < 0.50: return self.pair_swap(route)
        elif r < 0.75: return self.pickup_relocate(route)
        else: return self.delivery_relocate(route)

    def mutate_many(self, route):
        new_route = route[:]
        if self.n <= 100:
            times = random.randint(1,3)

        elif self.n <= 500:
            times = random.randint(2, 5)

        else:
            times = random.randint(3, 8)

        for _ in range(times):
            new_route = self.mutate(new_route)

        return new_route
        
    def random_route(self):
        remaining = list(range(1, self.n+1))
        onbus = []
        route = []
        load = 0

        while len(route) < 2*self.n:
            can_pickup = load < self.k and len(remaining) > 0
            can_delivery = len(onbus) > 0

            if not can_pickup and not can_delivery:
                greedy_route, _ = self.init_greedy_route()
                return greedy_route

            if can_pickup and can_delivery:
                pickup_weight = len(remaining)
                delivery_weight = len(onbus)
                choose_pickup = random.randint(1, pickup_weight + delivery_weight) <= pickup_weight
            else:
                choose_pickup = can_pickup

            if choose_pickup:
                idx = random.randrange(len(remaining))
                pickup = remaining[idx]
                remaining[idx] = remaining[-1]
                remaining.pop()

                route.append(pickup)
                onbus.append(pickup)
                load += 1
            else:
                idx = random.randrange(len(onbus))
                pickup = onbus[idx]
                last_pickup = onbus[-1]
                onbus[idx] = last_pickup
                onbus.pop()

                route.append(pickup + self.n)
                load -= 1

        return route

    def evaluate(self, route):
        if route is None or len(route) != 2*self.n: return INF
        return self.calc_cost(route)

    def request_id(self, node):
        if node <= self.n:
            return node
        return node - self.n

    def crossover(self, route1, route2):
        if self.n <= 1:
            return route1[:]

        seen = [0] * (self.n+1)
        request_order = []
        for node in route1:
            req = self.request_id(node)
            if not seen[req]:
                seen[req] = 1
                request_order.append(req)

        if len(request_order) != self.n:
            return route1[:]

        block_size = random.randint(1, self.n-1)
        left = random.randint(0, self.n-block_size)
        selected = set(request_order[left:left+block_size])

        child = []
        for node in route1:
            if self.request_id(node) in selected:
                child.append(node)
        for node in route2:
            if self.request_id(node) not in selected:
                child.append(node)

        if self.is_valid(child):
            return child
        return route1[:]

    def pair_relocate(self, route, max_attempts = 20):
        for _ in range(max_attempts):
            pickup = random.randint(1,self.n)
            delivery = pickup + self.n
            base = [x for x in route if x!=pickup and x!=delivery]
            L = len(base)

            p = random.randint(0, L)
            tmp = base[:p] + [pickup] + base[p:]
            q = random.randint(p+1, L+1)
            new_route = tmp[:q] + [delivery] + tmp[q:]

            if self.is_valid(new_route):
                return new_route
        return route[:]

    def pair_swap(self, route, max_attempts = 20):
        if self.n <= 1:
            return route[:]

        for _ in range(max_attempts):
            new_route = route[:]
            a,b = random.sample(range(1, self.n+1), 2)

            for idx, node in enumerate(route):
                if node == a:
                    new_route[idx] = b
                elif node == b:
                    new_route[idx] = a
                elif node == a+self.n:
                    new_route[idx] = b+self.n
                elif node == b+self.n:
                    new_route[idx] = a+self.n

            if self.is_valid(new_route):
                return new_route
        return route[:]

    def pickup_relocate(self, route, max_attempts = 20):
        for _ in range(max_attempts):
            pickup = random.randint(1,self.n)
            delivery = pickup + self.n
            base = []
            delivery_pos = None

            for node in route:
                if node == pickup:
                    continue
                if node == delivery:
                    delivery_pos = len(base)
                base.append(node)

            if delivery_pos is None:
                continue

            p = random.randint(0, delivery_pos)
            new_route = base[:p] + [pickup] + base[p:]

            if self.is_valid(new_route):
                return new_route
        return route[:]

    def delivery_relocate(self, route, max_attempts = 20):
        for _ in range(max_attempts):
            delivery = random.randint(1,self.n) + self.n
            pickup = delivery - self.n
            base = []
            pickup_pos = None

            for node in route:
                if node == delivery:
                    continue
                if node == pickup:
                    pickup_pos = len(base)
                base.append(node)

            if pickup_pos is None:
                continue

            p = random.randint(pickup_pos+1, len(base))
            new_route = base[:p] + [delivery] + base[p:]

            if self.is_valid(new_route):
                return new_route
        return route[:]

    def is_valid(self, route):
        if route is None or len(route) != 2*self.n:
            return False

        seen = [0] * (2*self.n+1)
        picked = [0] * (self.n+1)
        load = 0

        for node in route:
            if node < 1 or node > 2*self.n:
                return False
            if seen[node]:
                return False
            seen[node] = 1

            if node <= self.n:
                picked[node] = 1
                load += 1
                if load > self.k:
                    return False
            else:
                pickup = node - self.n
                if not picked[pickup]:
                    return False
                load -= 1

        return load == 0
        
    def calc_cost(self, route):
        if not route: return 0
        res = self.c[0][route[0]]
        for i in range(len(route)-1):
            res += self.c[route[i]][route[i+1]]
        res += self.c[route[-1]][0]
        return res

    def init_greedy_route(self):
        picked = [0 for _ in range(2*self.n+1)]
        load,last,total_cost = 0,0,0
        path = []
        onbus = set()

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

    def run(self):
        for _ in range(self.generations):
            end_time = time.time()
            if end_time - self.start_time >= self.timelimit:
                break

            scored = []
            for route in self.population:
                cost = self.evaluate(route)
                scored.append((cost, route))

            scored.sort(key=lambda x: x[0])

            cur_best_cost, cur_best_route = scored[0]
            # print(cur_best_cost)

            if cur_best_cost < self.best_cost:
                self.best_cost = cur_best_cost
                self.best_route = cur_best_route[:]

            new_population = []

            elite_count = min(self.elite_size, len(scored))

            for i in range(elite_count):
                child = scored[i][1][:]
                # if random.random() < self.mutation_rate:
                #     child = self.mutate(child)
                new_population.append(child)

            while len(new_population) < self.pop_size:
                parent1 = self.select(scored)
                parent2 = self.select(scored)

                if random.random() < self.crossover_rate:
                    child = self.crossover(parent1, parent2)
                else:
                    child = parent1[:]

                if random.random() < self.mutation_rate:
                    child = self.mutate_many(child)

                if not self.is_valid(child):
                    child = parent1[:]

                new_population.append(child)

            self.population = new_population

def solve():
    n,k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2*n+1)]
    n, best_route = GA(n,k,c).solve()

    print(n)
    print(*best_route)

def main():
    #Code
    t = 1
    for i in range(1,t+1):
        solve()

if __name__ == '__main__':
    main()
