import random


class HC:
    def __init__(self, n, k, c):
        self.n = n
        self.k = k
        self.c = c
   
    def solution(self):
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
       
        return route

    def pair_relocate(self, S):
        S1 = S[:]


        i = random.randint(1, self.n)
        S1.remove(i)
        S1.remove(i+self.n)


        pickup_pos = random.randint(0, len(S1))
        S1.insert(pickup_pos, i)


        delivery_pos = random.randint(pickup_pos+1, len(S1))
        S1.insert(delivery_pos, i+self.n)
   
        return S1

    def pair_swap(self, S):
        S1 = S[:]
        a = random.randint(1, self.n)
        b = random.randint(1, self.n)


        while a == b:
            b = random.randint(1, self.n)


        pos_a = S1.index(a)
        pos_ad = S1.index(a+self.n)


        pos_b = S1.index(b)
        pos_bd = S1.index(b+self.n)


        S1[pos_a], S1[pos_b] = S1[pos_b], S1[pos_a]
        S1[pos_ad], S1[pos_bd] = S1[pos_bd], S1[pos_ad]


        return S1

    def two_opt(self, S):
        S1 = S[:]


        i = random.randint(0, len(S1)-2)
        j = random.randint(i+1, len(S1)-1)


        S1[i:j+1] = S1[i:j+1][::-1]


        return S1

    def valid(self, S):
        load = 0
        visited = [0] * (2*self.n+1)
        for i in S:
            visited[i] = 1
            if i <= self.n:
                load += 1
                if load > self.k:
                    return False
            else:
                if not visited[i-self.n]:
                    return False
                load -= 1
        return True

    def cost(self, S):
        Cost = self.c[0][S[0]]
        for i in range(1, len(S)):
            Cost += self.c[S[i-1]][S[i]]
        Cost += self.c[S[-1]][0]
        return Cost

    def solve(self):
        S = self.solution()
        Cost = self.cost(S)


        for _ in range(50000):
            r = random.random()
           
            if r < 0.6:
                S1 = self.pair_relocate(S)
            elif r < 0.9:
                S1 = self.pair_swap(S)
            else:
                S1 = self.two_opt(S)


            costS1 = self.cost(S1)


            if self.valid(S1) and costS1 < Cost:
                Cost = costS1
                S = S1
   
        return self.n, S


def solve():
    n, k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2*n+1)]

    n, best_route = HC(n, k, c).solve()
    print(n)
    print(*best_route)


def main():
    t = 1
    for i in range(1, t+1):
        solve()


if __name__ == '__main__':
    main()
