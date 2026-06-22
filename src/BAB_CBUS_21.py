import sys


class BAB:
    def __init__(self, n, k, c):
        self.n = n
        self.k = k
        self.c = c
        self.N = 2 * n
        self.INF = 10**18

        self.best = self.INF
        self.best_route = []
        self.route = []
        self.picked = [False] * (n + 1)
        self.delivered = [False] * (n + 1)
        self.min_edge = self.find_min_edge()

    def find_min_edge(self):
        min_edge = self.INF
        for i in range(self.N + 1):
            for j in range(self.N + 1):
                if i != j:
                    min_edge = min(min_edge, self.c[i][j])
        return min_edge

    def calc_cost(self, route):
        if not route:
            return self.INF

        cost = self.c[0][route[0]]
        for i in range(len(route) - 1):
            cost += self.c[route[i]][route[i + 1]]
        cost += self.c[route[-1]][0]
        return cost

    def greedy_upper_bound(self):
        route = []
        visited = [False] * (self.N + 1)
        current = 0
        load = 0

        while len(route) < self.N:
            candidates = []

            if load < self.k:
                for node in range(1, self.n + 1):
                    if not visited[node]:
                        candidates.append(node)

            for node in range(self.n + 1, self.N + 1):
                pickup = node - self.n
                if not visited[node] and visited[pickup]:
                    candidates.append(node)

            if not candidates:
                break

            next_node = min(candidates, key=lambda node: self.c[current][node])
            visited[next_node] = True
            route.append(next_node)

            if next_node <= self.n:
                load += 1
            else:
                load -= 1
            current = next_node

        if len(route) == self.N:
            self.best_route = route[:]
            self.best = self.calc_cost(route)

    def dfs(self, pos, served, load, cost):
        if served == self.N:
            total = cost + self.c[pos][0]
            if total < self.best:
                self.best = total
                self.best_route = self.route[:]
            return

        remain = self.N - served
        lower_bound = cost + (remain + 1) * self.min_edge
        if lower_bound >= self.best:
            return

        if load < self.k:
            for node in range(1, self.n + 1):
                if self.picked[node]:
                    continue

                self.picked[node] = True
                self.route.append(node)
                self.dfs(
                    node,
                    served + 1,
                    load + 1,
                    cost + self.c[pos][node],
                )
                self.route.pop()
                self.picked[node] = False

        for node in range(1, self.n + 1):
            if (not self.picked[node]) or self.delivered[node]:
                continue

            delivery = node + self.n
            self.delivered[node] = True
            self.route.append(delivery)
            self.dfs(
                delivery,
                served + 1,
                load - 1,
                cost + self.c[pos][delivery],
            )
            self.route.pop()
            self.delivered[node] = False

    def solve(self):
        sys.setrecursionlimit(max(1000, self.N + 50))
        self.greedy_upper_bound()
        self.dfs(0, 0, 0, 0)
        return self.n, self.best_route


def solve():
    n, k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2 * n + 1)]

    n, best_route = BAB(n, k, c).solve()
    print(n)
    print(*best_route)


def main():
    solve()


if __name__ == "__main__":
    main()
