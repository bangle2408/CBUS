class TS:
    def __init__(self, n, k, c):
        self.tabu = []
        self.tabu_size = 20
        self.n = n
        self.k = k
        self.c = c

    def greedy(self):
        route = []
        visited = [False]*(2*self.n + 1)
        visited[0] = True
        best_nxt = None
        cur = 0
        load = 0
        cost = 0
        for _ in range(2*self.n):
            best_nxt = None
            best_cost = 1e15
            for nxt in range(1, 2*self.n + 1):
                if visited[nxt]:
                    continue
                if nxt > self.n:
                    pick_up = nxt - self.n
                    if visited[pick_up] == False:
                        continue
                else:
                    if load == self.k:
                        continue
                if self.c[cur][nxt] < best_cost:
                    best_cost = self.c[cur][nxt]
                    best_nxt = nxt
            visited[best_nxt] = True
            if best_nxt <= self.n:
                load += 1
            else:
                load -= 1


            cost += self.c[cur][best_nxt]
            cur = best_nxt
            route.append(best_nxt)
        cost += self.c[cur][0]


        return route

    def evaluate(self, route):
        cost = self.c[0][route[0]]
        for x in range(len(route)-1):
            cost += self.c[route[x]][route[x+1]]
        cost += self.c[route[-1]][0]
        return cost

    def feasible(self, route):
        load = 0
        picked = [False]*(self.n+1)
        for x in route:
            if 1 <= x <= self.n:
                load += 1
                picked[x] = True
            elif x > self.n:
                pick = x - self.n
                if not picked[pick]:
                    return False
                load -= 1
            if load > self.k:
                return False
            if load < 0:
                return False
        return True

    def relocate(self, route, i, j):
        new_route = route[:]
        modified = new_route.pop(i)


        if i < j:
            j -= 1


        new_route.insert(j, modified)
        return new_route

    def solve(self):
        temp_opt_route = self.greedy()
        temp_best_cost = self.evaluate(temp_opt_route)
        improved = True
        while improved:
            improved = False
            for i in range(2*self.n):
                for j in range(i+2, min(2*self.n, i+50)):
                    if (i, j) in self.tabu:
                        continue


                    new_route = self.relocate(temp_opt_route, i, j)
                    if self.feasible(new_route):
                        new_cost = self.evaluate(new_route)
                        if new_cost < temp_best_cost:
                            temp_best_cost = new_cost
                            temp_opt_route = new_route
                            improved = True
                            self.tabu.append((i, j))
                            if len(self.tabu) > self.tabu_size:
                                self.tabu.pop(0)


        return self.n, temp_opt_route


def solve():
    n, k = map(int, input().split())
    c = []
    for _ in range(2*n + 1):
        c.append(list(map(int, input().split())))

    n, best_route = TS(n, k, c).solve()
    print(n)
    print(*best_route)


def main():
    t = 1
    for i in range(1, t+1):
        solve()


if __name__ == '__main__':
    main()
