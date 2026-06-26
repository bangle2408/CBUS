import time

from ortools.sat.python import cp_model


class CP:
    def __init__(self, n, k, c, timelimit=None):
        self.n = n
        self.k = k
        self.c = c
        self.N = 2 * n
        self.timelimit = None if timelimit is None else float(timelimit)
        self.start_time = time.time()

    def remaining_time(self):
        if self.timelimit is None:
            return None

        elapsed = time.time() - self.start_time
        return max(0.0, self.timelimit - elapsed)

    def is_tle(self):
        return (
            self.timelimit is not None
            and time.time() - self.start_time >= self.timelimit
        )

    def build_route(self, solver, x):
        route = []
        current = 0
        seen = {0}

        while True:
            next_node = None
            for node in range(self.N + 1):
                if node != current and solver.Value(x[current][node]):
                    next_node = node
                    break

            if next_node is None or next_node == 0:
                break

            if next_node in seen:
                break

            route.append(next_node)
            seen.add(next_node)
            current = next_node

        return route

    def solve(self):
        if self.is_tle():
            return float("nan"), "TLE"

        model = cp_model.CpModel()
        m = max(2000, self.N + self.k + 5)

        x = [
            [
                model.NewBoolVar(f"X[{i}][{j}]")
                for j in range(self.N + 1)
            ]
            for i in range(self.N + 1)
        ]
        w = [
            model.NewIntVar(0, self.k, f"w[{i}]")
            for i in range(self.N + 1)
        ]
        u = [
            model.NewIntVar(0, self.N, f"u[{i}]")
            for i in range(self.N + 1)
        ]
        q = [0] + [1] * self.n + [-1] * self.n

        for i in range(self.N + 1):
            for j in range(self.N + 1):
                if i == j:
                    continue
                model.Add(w[j] >= w[i] + q[j] - m * (1 - x[i][j]))
                model.Add(w[j] <= w[i] + q[j] + m * (1 - x[i][j]))

        for i in range(1, self.n + 1):
            model.Add(u[i + self.n] >= u[i] + 1)

        for i in range(self.N + 1):
            for j in range(1, self.N + 1):
                if i != j:
                    model.Add(u[j] >= u[i] + 1 - m * (1 - x[i][j]))

        for i in range(self.N + 1):
            model.Add(
                sum(x[i][j] for j in range(self.N + 1) if i != j) == 1
            )

        for j in range(self.N + 1):
            model.Add(
                sum(x[i][j] for i in range(self.N + 1) if i != j) == 1
            )

        for i in range(self.N + 1):
            model.Add(x[i][i] == 0)

        model.Add(u[0] == 0)
        model.Add(w[0] == 0)

        cost = sum(
            self.c[i][j] * x[i][j]
            for i in range(self.N + 1)
            for j in range(self.N + 1)
        )
        model.Minimize(cost)

        solver = cp_model.CpSolver()
        time_left = self.remaining_time()
        if time_left is not None:
            if time_left <= 0:
                return float("nan"), "TLE"

            solver.parameters.max_time_in_seconds = time_left

        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            if self.is_tle() or (
                status == cp_model.UNKNOWN and self.timelimit is not None
            ):
                return float("nan"), "TLE"

            return self.n, []

        return self.n, self.build_route(solver, x)


def solve():
    n, k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2 * n + 1)]

    n, best_route = CP(n, k, c).solve()
    if best_route == "TLE":
        print(n)
        print(best_route)
        return

    if not best_route:
        print("No solution")
        return

    print(n)
    print(*best_route)


def main():
    solve()


if __name__ == "__main__":
    main()
