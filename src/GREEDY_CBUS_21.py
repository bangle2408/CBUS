class GREEDY:
    def __init__(self, n, k, c):
        self.n = n
        self.k = k
        self.c = c

    def solve(self):
        current = 0
        load = 0
        route = []
        visited = [0] * (2*self.n+1)


        while True:
            F = []
   
            if load < self.k:
                for i in range(1, self.n+1):
                    if not visited[i]:
                        F.append(i)
   
            for i in range(self.n+1, 2*self.n+1):
                if not visited[i] and visited[i-self.n]:
                    F.append(i)
   
            if not F:
                break


            min_dis = float('inf')


            next = min(F, key=lambda x: self.c[current][x])
   
            visited[next] = 1
            route.append(next)


            if next <= self.n:
                load += 1
            else:
                load -= 1


            current = next


        return self.n, route


def solve():
    n, k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2*n+1)]

    n, best_route = GREEDY(n, k, c).solve()
    print(n)
    for i in best_route:
        print(i, end=" ")


def main():
    t = 1
    for i in range(1, t+1):
        solve()


if __name__ == '__main__':
    main()
