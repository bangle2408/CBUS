import sys


class DP:
    def __init__(self, n, k, c):
        self.n = n
        self.k = k
        self.c = c
        self.N = 2 * n
        self.full = (1 << self.N) - 1
        self.INF = 10**18
        self.memo = {}
        self.choice = {}

    def get_load(self, mask):
        pickup_mask = mask & ((1 << self.n) - 1)
        delivery_mask = mask >> self.n
        return pickup_mask.bit_count() - delivery_mask.bit_count()

    def solve_state(self, cur, mask):
        if mask == self.full:
            return self.c[cur][0]

        key = (cur, mask)
        if key in self.memo:
            return self.memo[key]

        load = self.get_load(mask)
        ans = self.INF
        best_next = None

        for nxt in range(1, self.N + 1):
            bit = 1 << (nxt - 1)
            if mask & bit:
                continue

            if nxt <= self.n:
                if load == self.k:
                    continue
            else:
                pickup = nxt - self.n
                if not (mask & (1 << (pickup - 1))):
                    continue

            new_cost = self.c[cur][nxt] + self.solve_state(nxt, mask | bit)
            if new_cost < ans:
                ans = new_cost
                best_next = nxt

        self.memo[key] = ans
        if best_next is not None:
            self.choice[key] = best_next
        return ans

    def build_route(self):
        route = []
        cur = 0
        mask = 0

        while mask != self.full:
            nxt = self.choice.get((cur, mask))
            if nxt is None:
                break

            route.append(nxt)
            mask |= 1 << (nxt - 1)
            cur = nxt

        return route

    def solve(self):
        sys.setrecursionlimit(max(1000, self.N + 50))
        self.solve_state(0, 0)
        return self.n, self.build_route()


CBUSDP = DP


def solve():
    n, k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2 * n + 1)]

    n, best_route = DP(n, k, c).solve()
    print(n)
    print(*best_route)


def main():
    solve()


if __name__ == "__main__":
    main()
