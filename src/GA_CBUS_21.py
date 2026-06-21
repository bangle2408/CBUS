import sys,time,io,os
import random
from heapq import heapify, heappush, heappop

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
        best_cost, best_gene = random.choice(scored)

        for _ in range(self.tournament_size-1):
            cost, gene = random.choice(scored)

            if cost < best_cost:
                best_cost = cost
                best_gene = gene

        return best_gene

    def init_population(self):
        population = []

        greedy_gene, greedy_cost = self.init_greedy_route()
        population.append(greedy_gene)
        self.best_gene = greedy_gene[:]
        self.best_route = greedy_gene[:]
        self.best_cost = greedy_cost

        greedy_varients = self.pop_size//3
        for _ in range(greedy_varients):
            gene = greedy_gene[:]
            mutation_times = random.randint(1,5)

            for _ in range(mutation_times):
                gene = self.mutate(gene)

            population.append(gene)

        while len(population)<self.pop_size:
            population.append(self.random_gene())

        return population

    def mutate(self, gene):
        r = random.random()

        if r < 0.3: return self.swap_mutation(gene)
        elif r < 0.55: return self.reverse_mutation(gene)
        elif r < 0.8: return self.insert_mutation(gene)
        else: return self.pair_mutation(gene)

    def mutate_many(self, gene):
        new_gene = gene[:]
        if self.n <= 100:
            times = random.randint(1,3)

        elif self.n <= 500:
            times = random.randint(2, 5)

        else:
            times = random.randint(3, 8)

        for _ in range(times):
            new_gene = self.mutate(new_gene)

        return new_gene
        
    def random_gene(self):
        gene = list(range(1, self.n * 2 + 1))
        random.shuffle(gene)
        return gene

    def evaluate(self, gene):    
        if gene is None: return INF

        route = self.decode_gene(gene)
        if route is None: return INF

        return self.calc_cost(route)

    def insert_mutation(self, gene):
        m = len(gene)
        new_gene = gene[:]

        i = random.randint(0,m-1)
        node = new_gene.pop(i)
        j = random.randint(0,m-2)
        new_gene.insert(j, node)

        return new_gene

    def swap_mutation(self, gene):
        m = len(gene)
        new_gene = gene[:]

        i,j = random.sample(range(m), 2)

        new_gene[i], new_gene[j] = new_gene[j], new_gene[i]

        return new_gene

    def reverse_mutation(self, gene):
        new_gene = gene[:]
        m = len(gene)
        
        i,j = sorted(random.sample(range(m), 2))
        new_gene[i:j+1] = new_gene[i:j+1][::-1]

        return new_gene

    def pair_mutation(self, gene):
        pickup = random.randint(1, self.n)
        delivery = pickup + self.n

        base = [x for x in gene if x!=pickup and x!=delivery]
        pos = random.randint(0,len(base))
        new_gene = base[:pos] + [pickup,delivery] + base[pos:]
        return new_gene

    def crossover(self, gene1, gene2):
        m = len(gene1)

        left = random.randint(0, m-2)
        right = random.randint(left+1, m-1)

        child = [-1] * m
        used = set()

        for i in range(left, right+1):
            child[i] = gene1[i]
            used.add(gene1[i])

        idx = (right + 1)%m
        for j in range(m):
            node = gene2[(right+1+j)%m]
            if node in used: continue
            used.add(node)
            child[idx] = node
            idx = (idx+1)%m

        return child

    def decode_gene(self, gene):
        if gene is None: return None

        if len(gene) != self.n * 2: return None 

        rank = [0] * (self.n * 2 +1)
        seen = [0] * (self.n * 2 +1)
        
        for i,node in enumerate(gene):
            if node < 1 or node > 2*self.n:
                return None
            if seen[node]: return None
            seen[node] = 1
            rank[node] = i

        pickupheap = []
        deliveryheap = []

        for pickup in range(1, self.n+1):
            pickupheap.append((rank[pickup], pickup))
        heapify(pickupheap)
        heapify(deliveryheap)

        route = []
        load = 0

        while len(route) < 2*self.n:
            can_pickup = load < self.k and len(pickupheap) > 0
            can_delivery = len(deliveryheap) > 0

            if can_pickup and can_delivery:
                if pickupheap[0][0] <= deliveryheap[0][0]:
                    _,pickup = heappop(pickupheap)

                    route.append(pickup)
                    load += 1

                    delivery = pickup + self.n
                    heappush(deliveryheap, (rank[delivery], delivery))
                else:
                    _, delivery = heappop(deliveryheap)

                    route.append(delivery)
                    load -= 1
            elif can_pickup:
                _,pickup = heappop(pickupheap)

                route.append(pickup)
                load += 1

                delivery = pickup + self.n
                heappush(deliveryheap, (rank[delivery], delivery))
            elif can_delivery:
                _, delivery = heappop(deliveryheap)

                route.append(delivery)
                load -= 1
            else: return None

        return route
        
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
            for gene in self.population:
                cost = self.evaluate(gene)
                scored.append((cost, gene))

            scored.sort(key=lambda x: x[0])

            cur_best_cost, cur_best_gene = scored[0]
            # print(cur_best_cost)

            if cur_best_cost < self.best_cost:
                self.best_cost = cur_best_cost
                self.best_route = self.decode_gene(cur_best_gene)

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
