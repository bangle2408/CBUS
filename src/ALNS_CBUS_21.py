import sys,time,io,os
from collections import defaultdict
import random
import math

INF = 1<<60

class ALNS_SA:
    def __init__(self, n, k, c, temperature = 5, stop_temperture = 1e-4, iterations = 50000, alpha = 0.995, timelimit = 290):
        self.n = n 
        self.k = k
        self.c = c
        self.T = temperature
        self.Tmin = stop_temperture
        self.start_time = time.time()
        self.timelimit = timelimit
        self.iterations = iterations
        self.alpha = alpha

        self.destroy_operators = [
                self.destroy_related,
                self.destroy_worst,
                self.destroy_segment,
                self.destroy_random,
        ]

        self.repair_operators = [
                self.repair_greedy,
                self.repair_regret,
                self.repair_random_order,
        ]

        self.destroy_weights = [1.4, 1.3, 1.0, 0.8]
        self.repair_weights = [1.5, 1.0, 0.4]
        
        self.destroy_scores = [0.0] * len(self.destroy_operators)
        self.repair_scores = [0.0] * len(self.repair_operators)
        
        self.destroy_used = [0] * len(self.destroy_operators)
        self.repair_used = [0] * len(self.repair_operators)

        self.alns_iter = 0
        self.alns_update_period = 100
        self.alns_rho = 0.2

        self.cur_route, self.cur_cost = self.init_greedy_route()
        # print("init_cost:" + str(self.cur_cost))
        self.best_route = self.cur_route[:]
        self.best_cost = self.cur_cost

        if self.n <= 100:
            self.near_node_limit = 24
            self.near_pair_limit = 12
        elif self.n <= 200:
            self.near_node_limit = 22
            self.near_pair_limit = 10
        elif self.n <= 500:
            self.near_node_limit = 18
            self.near_pair_limit = 8
        else:
            self.near_node_limit = 14
            self.near_pair_limit = 7

        self.build_nearest_nodes()

    def solve(self):
        self.run()
        return self.n, self.best_route

    def get_neighbor(self, route):
        remove_count, random_samples = self.choose_parameters()
        remove_count = min(remove_count, self.n)

        d_idx = self.weighted_choice(self.destroy_weights)
        r_idx = self.weighted_choice(self.repair_weights)

        destroy = self.destroy_operators[d_idx]
        repair = self.repair_operators[r_idx]

        base, removed = destroy(route, remove_count)

        if not removed:
            return route[:], d_idx, r_idx, False

        new_route = repair(base, removed, random_samples)

        if new_route is None:
            return route[:], d_idx, r_idx, False

        if not self.is_valid(new_route):
            return route[:], d_idx, r_idx, False

        return new_route, d_idx, r_idx, True

    def unique_limited(self, values, limit, low, high):
        seen = set()
        res = []

        for x in values:
            if x < low or x > high:
                continue

            if x in seen:
                continue

            seen.add(x)
            res.append(x)

            if len(res) >= limit:
                break

        return res

    def build_nearest_nodes(self):
        N = 2 * self.n + 1
        self.nearest_nodes = []

        all_nodes = list(range(1, N))

        for u in range(N):
            row = self.c[u]

            arr = sorted(all_nodes, key=lambda v: row[v])

            if 1 <= u < N:
                arr = [v for v in arr if v != u]

            self.nearest_nodes.append(arr[:self.near_node_limit])

    def build_pos(self, route):
        pos = [-1] * (2*self.n+1)
        for i, node in enumerate(route):
            pos[node] = i

        return pos

    def calc_load_before(self, route):
        load = 0
        a = []
        for node in route:
            a.append(load)
            if node <= self.n:
                load += 1
            else: load -= 1

        a.append(load)
        return a

    def build_max_segment_tree(self, arr):
        size=1
        while size < len(arr):
            size<<=1

        seg = [-INF] * (2*size)
        for i, value in enumerate(arr):
            seg[i+size] = value

        for i in range(size-1, 0, -1):
            seg[i] = max(seg[i << 1], seg[i << 1 | 1])

        return seg, size

    def range_max(self, seg, size, l, r):
        res = -INF

        l += size
        r += size

        while l<r:
            if l&1: 
                res = max(res, seg[l])
                l += 1
            if r&1:
                r -= 1
                res = max(res, seg[r])

            l >>= 1
            r >>= 1

        return res

    def capacity_check_after_insert(self, seg, size, p, q):
        return self.range_max(seg, size, p, q) + 1 <= self.k

    def insert_delta(self, route, pickup, p, q):
        delivery = pickup + self.n
        L = len(route)

        if L == 0:
            return (
                self.c[0][pickup]
                + self.c[pickup][delivery]
                + self.c[delivery][0]
            )

        A = route[p - 1] if p > 0 else 0
        B = route[p] if p < L else 0

        if q == p + 1:
            return (
                self.c[A][pickup]
                + self.c[pickup][delivery]
                + self.c[delivery][B]
                - self.c[A][B]
            )

        delta_pick = (
            self.c[A][pickup]
            + self.c[pickup][B]
            - self.c[A][B]
        )

        C = route[q - 2]
        D = route[q - 1] if q - 1 < L else 0

        delta_delivery = (
            self.c[C][delivery]
            + self.c[delivery][D]
            - self.c[C][D]
        )

        return delta_pick + delta_delivery

    def choose_parameters(self):
        r = random.random()

        if r < 0.70:
            if self.n <= 100:
                return random.randint(2, 6), 24
            elif self.n <= 200:
                return random.randint(2, 6), 20
            elif self.n <= 500:
                return random.randint(2, 5), 16
            else:
                return random.randint(2, 5), 12

        if r < 0.95:
            if self.n <= 100:
                return random.randint(8, 16), 20
            elif self.n <= 200:
                return random.randint(10, 24), 18
            elif self.n <= 500:
                return random.randint(15, 35), 14
            else:
                return random.randint(20, 45), 10

        if self.n <= 100:
            return random.randint(18, 30), 16
        elif self.n <= 200:
            return random.randint(25, 45), 14
        elif self.n <= 500:
            return random.randint(35, 65), 10
        else:
            return random.randint(45, 75), 8

    def weighted_choice(self, weights):
        total = sum(weights)
        p = random.random() * total
        
        cumutative = 0.0
        for i, w in enumerate(weights):
            cumutative += w
            if cumutative >= p:
                return i

        return len(weights) - 1

    def reward_operator(self, d_idx, r_idx, reward):
        self.destroy_scores[d_idx] += reward
        self.repair_scores[r_idx] += reward

        self.destroy_used[d_idx] += 1
        self.repair_used[r_idx] += 1

        self.alns_iter += 1

        if self.alns_iter % self.alns_update_period != 0:
            return

        for i in range(len(self.destroy_weights)):
            if self.destroy_used[i] > 0:
                avg = self.destroy_scores[i] / self.destroy_used[i]
                self.destroy_weights[i] = (
                    (1.0 - self.alns_rho) * self.destroy_weights[i]
                    + self.alns_rho * avg
                )

                self.destroy_weights[i] = min(20.0, max(0.05, self.destroy_weights[i]))

        for i in range(len(self.repair_weights)):
            if self.repair_used[i] > 0:
                avg = self.repair_scores[i] / self.repair_used[i]
                self.repair_weights[i] = (
                    (1.0 - self.alns_rho) * self.repair_weights[i]
                    + self.alns_rho * avg
                )

                self.repair_weights[i] = min(20.0, max(0.05, self.repair_weights[i]))

        self.destroy_scores = [0.0] * len(self.destroy_operators)
        self.repair_scores = [0.0] * len(self.repair_operators)

        self.destroy_used = [0] * len(self.destroy_operators)
        self.repair_used = [0] * len(self.repair_operators)

    def remove_nodes(self, route, node_list):
        mark = [0] * (2*self.n+1)
        for p in node_list:
            mark[p] = 1
            mark[p+self.n] = 1

        return [x for x in route if not mark[x]]

    def insert_nodes(self, route, pickup, x, y):
        delivery = pickup + self.n
        tmp = route[:x] + [pickup] + route[x:]
        return tmp[:y] + [delivery] + tmp[y:]

    def best_two_insertion(self, route, pickup, random_samples, base_cost, pos, seg, seg_size):
        delivery = pickup + self.n
        L = len(route)

        best_cost = INF
        second_cost = INF

        best_pos = None
        second_pos = None

        tried = set()

        def consider(p, q):
            nonlocal best_cost, second_cost, best_pos, second_pos

            if p < 0 or p > L:
                return

            if q <= p or q > L + 1:
                return

            if (p, q) in tried:
                return

            tried.add((p, q))

            if not self.capacity_check_after_insert(seg, seg_size, p, q):
                return

            new_cost = base_cost + self.insert_delta(route, pickup, p, q)

            if new_cost < best_cost:
                second_cost = best_cost
                second_pos = best_pos

                best_cost = new_cost
                best_pos = (p, q)

            elif new_cost < second_cost:
                second_cost = new_cost
                second_pos = (p, q)

        #random
        for _ in range(random_samples):
            p = random.randint(0, L)
            q = random.randint(p + 1, L + 1)

            consider(p, q)

        #pickup va delivery lien nhau
        for _ in range(max(2, random_samples // 3)):
            p = random.randint(0, L)
            consider(p, p + 1)

        #candidate gan voi pickup
        p_candidates = [0, L]

        for v in self.nearest_nodes[pickup]:
            idx = pos[v]

            if idx != -1:
                p_candidates.append(idx)
                p_candidates.append(idx + 1)

        p_candidates = self.unique_limited(p_candidates,self.near_pair_limit,0,L)

        # candidate gan delivery
        q_candidates = [L + 1]

        for v in self.nearest_nodes[delivery]:
            idx = pos[v]

            if idx != -1:
                q_candidates.append(idx + 1)
                q_candidates.append(idx + 2)

        q_candidates = self.unique_limited(q_candidates,self.near_pair_limit,1,L + 1)

        for p in p_candidates:
            consider(p, p + 1)

            for q in q_candidates:
                if q > p:
                    consider(p, q)

        #fallback
        consider(L, L + 1)

        return best_cost, best_pos, second_cost, second_pos

    def best_insertion(self, route, pickup, random_samples, base_cost, pos, seg, seg_size):
        best_cost, best_pos, _, _ = self.best_two_insertion(route,pickup,random_samples,base_cost,pos,seg,seg_size)

        if best_pos is None:
            return None

        return best_cost, best_pos
    
    def calc_regret(self, route, pickup, random_samples, base_cost, pos, seg, seg_size):
        best_cost, best_pos, second_cost, second_pos = self.best_two_insertion(route,pickup,random_samples,base_cost,pos,seg,seg_size)

        if best_pos is None:
            return None

        if second_pos is None:
            regret = 0
        else:
            regret = second_cost - best_cost

        return regret, best_cost, best_pos

    def repair_greedy(self, base, removed, random_samples):
        remaining = removed[:]

        while remaining:
            base_cost = self.calc_cost(base)
            pos = self.build_pos(base)
            load_before = self.calc_load_before(base)
            seg, seg_size = self.build_max_segment_tree(load_before)

            best_pickup = None
            best_cost = INF
            best_pos = None

            for pickup in remaining:
                info = self.best_insertion(base,pickup,random_samples,base_cost,pos,seg,seg_size)

                if info is None:
                    continue

                cost, candidate_pos = info

                if cost < best_cost:
                    best_cost = cost
                    best_pickup = pickup
                    best_pos = candidate_pos

            if best_pickup is None:
                return None

            p, q = best_pos
            base = self.insert_nodes(base, best_pickup, p, q)
            remaining.remove(best_pickup)

        return base

    def repair_regret(self, base, removed, random_samples):
        remaining = removed[:]

        while remaining:
            base_cost = self.calc_cost(base)
            pos = self.build_pos(base)
            load_before = self.calc_load_before(base)
            seg, seg_size = self.build_max_segment_tree(load_before)

            best_pickup = None
            best_regret = -1
            best_cost = INF
            best_pos = None

            for pickup in remaining:
                info = self.calc_regret(base,pickup,random_samples,base_cost,pos,seg,seg_size)

                if info is None:
                    continue

                regret, cost, candidate_pos = info

                if regret > best_regret or (regret == best_regret and cost < best_cost):
                    best_regret = regret
                    best_cost = cost
                    best_pickup = pickup
                    best_pos = candidate_pos

            if best_pickup is None:
                return None

            p, q = best_pos
            base = self.insert_nodes(base, best_pickup, p, q)
            remaining.remove(best_pickup)

        return base

    def repair_random_order(self, base, removed, random_samples):
        remaining = removed[:]
        random.shuffle(remaining)

        for pickup in remaining:
            base_cost = self.calc_cost(base)
            pos = self.build_pos(base)
            load_before = self.calc_load_before(base)
            seg, seg_size = self.build_max_segment_tree(load_before)

            info = self.best_insertion(base,pickup,random_samples,base_cost,pos,seg,seg_size)

            if info is None:
                return None

            _, candidate_pos = info
            p, q = candidate_pos

            base = self.insert_nodes(base, pickup, p, q)

        return base

    def destroy_random(self, route, remove_count):
        removed = random.sample(range(1, self.n+1), remove_count)
        base = self.remove_nodes(route, removed)

        return base, removed

    def destroy_segment(self, route, remove_count):
        L = len(route)
        remove_length = min(L, max(2*remove_count, L//25))
        start = random.randint(0, L-1)
        end = min(L, start + remove_length)

        removed = []
        used = set()

        for node in route[start:end]:
            if node <= self.n:
                p = node
            else: p = node - self.n

            if p not in used:
                used.add(p)
                removed.append(p)
                if len(removed) >= remove_count: break

        while len(removed) < remove_count:
            p = random.randint(1,self.n)
            if p not in used:
                used.add(p)
                removed.append(p)

        base = self.remove_nodes(route, removed)

        return base, removed

    def calc_saving(self, route, pos, pickup):
        delivery = pickup + self.n
        a = pos[pickup]
        b = pos[delivery]

        if a > b: a,b = b,a
        L = len(route)
        prev_a = route[a-1] if a>0 else 0
        next_a = route[a+1] if a+1<L else 0

        prev_b = route[b-1] if b>0 else 0
        next_b = route[b+1] if b+1<L else 0

        if b == a+1:
            before = (self.c[prev_a][pickup] + self.c[pickup][delivery] + self.c[delivery][next_b])
            after = self.c[prev_a][next_b]
            return before - after

        before = (self.c[prev_a][pickup] + self.c[pickup][next_a] + self.c[prev_b][delivery] + self.c[delivery][next_b])
        after = self.c[prev_a][next_a] + self.c[prev_b][next_b]
        return before - after

    def destroy_worst(self, route, remove_count):
        remove_count = min(remove_count, self.n)

        pos = self.build_pos(route)

        sample_size = min(self.n, remove_count*5)
        sampled = random.sample(range(1, self.n+1), sample_size)

        scored = []
        for p in sampled:
            saving = self.calc_saving(route, pos, p)
            scored.append((saving,p))

        scored.sort(reverse = True)
        removed = [p for _,p in scored[:remove_count]]
        base = self.remove_nodes(route, removed)
        return base, removed

    def destroy_related(self, route, remove_count):
        remove_count = min(remove_count, self.n)

        seed = random.randint(1, self.n)

        sample_size = min(self.n, max(remove_count * 10, remove_count + 1))
        sampled = random.sample(range(1, self.n + 1), sample_size)

        scored = []

        for p in sampled:
            if p == seed:
                continue

            score = self.c[seed][p] + self.c[seed + self.n][p + self.n]
            scored.append((score, p))

        scored.sort()

        removed = [seed]
        used = {seed}

        for _, p in scored:
            if len(removed) >= remove_count:
                break

            if p not in used:
                used.add(p)
                removed.append(p)

        while len(removed) < remove_count:
            p = random.randint(1, self.n)

            if p not in used:
                used.add(p)
                removed.append(p)

        base = self.remove_nodes(route, removed)

        return base, removed

    def calc_prob(self, T, cost):
        if T <= 0: return 0.0
        delta = -(cost/T)
        if delta <= -650: return 0
        return math.exp(delta)

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
        if not route: return 0
        res = self.c[0][route[0]]
        for i in range(len(route)-1):
            res += self.c[route[i]][route[i+1]]
        res += self.c[route[-1]][0]
        return res

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

    def run(self):
        while self.iterations > 0:
            now = time.time()

            if now - self.start_time >= self.timelimit:
                break

            old_cur_cost = self.cur_cost

            new_route, d_idx, r_idx, ok = self.get_neighbor(self.cur_route[:])

            if not ok:
                self.reward_operator(d_idx, r_idx, 0.0)
                self.iterations -= 1
                continue

            new_cost = self.calc_cost(new_route)
            delta = new_cost - self.cur_cost

            accepted = False

            if delta <= 0:
                accepted = True
            elif self.T > self.Tmin and random.random() <= self.calc_prob(self.T, delta):
                accepted = True

            if accepted:
                self.cur_route = new_route[:]
                self.cur_cost = new_cost

            new_global_best = False

            if self.cur_cost < self.best_cost:
                self.best_route = self.cur_route[:]
                self.best_cost = self.cur_cost
                new_global_best = True

            if new_global_best:
                reward = 15.0
            elif accepted and self.cur_cost < old_cur_cost:
                reward = 6.0
            elif accepted:
                reward = 1.0
            else:
                reward = 0.05

            self.reward_operator(d_idx, r_idx, reward)

            if self.T > self.Tmin:
                self.T *= self.alpha

            self.iterations -= 1

def solve():
    n,k = map(int, input().split())
    c = [list(map(int, input().split())) for _ in range(2*n+1)]
    n,best_route = ALNS_SA(n,k,c).solve()
    print(n)
    print(*best_route)

def main():
    #Code
    t = 1
    for i in range(1,t+1):
        solve()

if __name__ == '__main__':
    main()
