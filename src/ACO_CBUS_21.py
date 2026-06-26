import random
from math import pow
from bisect import bisect_left

class Route:
    def __init__(self, path=None, cost=0):
        self.path = path if path is not None else []
        self.cost = cost

class ACO:
   def __init__(self, n, k, c):
      random.seed(1)
      self.n = n
      self.k = k
      self.N = 2 * n
      self.c = c
      self.tau = []
      self.nearestPickup = []

      self.buildNearestPickupList()
      self.tau = [[1.0] * (self.N + 1) for _ in range(self.N + 1)]
      self.best = self.greedyInitialRoute()

   def calcCost(self, path):
      total = 0
      cur = 0


      for x in path:
          total += self.c[cur][x]
          cur = x
      total += self.c[cur][0]
      return total

   def isFeasible(self, path):
      picked = [0] * (self.n + 1)
      delivered = [0] * (self.n + 1)
      load = 0


      for x in path:
          if 1 <= x <= self.n:
              if picked[x]:
                  return False
              picked[x] = 1
              load += 1
              if load > self.k:
                  return False


          else:
              p = x - self.n


              if p < 1 or p > self.n:
                  return False
              if not picked[p]:
                  return False
              if delivered[p]:
                  return False
              delivered[p] = 1
              load -= 1


      for i in range(1, self.n + 1):
          if not picked[i] or not delivered[i]:
              return False
      return True

   def greedyInitialRoute(self):
      path = []
      picked = [0] * (self.n + 1)
      delivered = [0] * (self.n + 1)
      onboard = []
      cur = 0
      load = 0


      while len(path) < 2 * self.n:
          bestNode = -1
          bestDist = 10 ** 18


          for p in onboard:
              if not delivered[p]:
                  node = p + self.n
                  if self.c[cur][node] < bestDist:
                      bestDist = self.c[cur][node]
                      bestNode = node


          if load < self.k:
              for p in range(1, self.n + 1):
                  if not picked[p]:
                      if self.c[cur][p] < bestDist:
                          bestDist = self.c[cur][p]
                          bestNode = p
          nextNode = bestNode
          path.append(nextNode)


          if nextNode <= self.n:
              picked[nextNode] = 1
              onboard.append(nextNode)
              load += 1
             
          else:
              p = nextNode - self.n
              delivered[p] = 1
              load -= 1
              onboard.remove(p)
          cur = nextNode
      return Route(path, self.calcCost(path))

   def buildAntRoute(self, alpha, beta, q0, pickupCandidateLimit):
      path = []
      picked = [0] * (self.n + 1)
      delivered = [0] * (self.n + 1)
      onboard = []
      cur = 0
      load = 0


      while len(path) < 2 * self.n:
          candidates = []


          for p in onboard:
              if not delivered[p]:
                  candidates.append(p + self.n)


          if load < self.k:
              cnt = 0


              for p in self.nearestPickup[cur]:
                  if not picked[p]:
                      candidates.append(p)
                      cnt += 1
                      if cnt >= pickupCandidateLimit:
                          break


          if not candidates:
              if load < self.k:
                  for p in range(1, self.n + 1):
                      if not picked[p]:
                          candidates.append(p)
                          break


              else:
                  for p in onboard:
                      if not delivered[p]:
                          candidates.append(p + self.n)
                          break


          if random.random() < q0:
              bestScore = -1
              nextNode = -1


              for v in candidates:
                  pheromone = pow(self.tau[cur][v], alpha)
                  visibility = pow(1.0 / (self.c[cur][v] + 1.0), beta)
                  score = pheromone * visibility
                  if score > bestScore:
                      bestScore = score
                      nextNode = v


          else:
              weight = []
              total = 0


              for v in candidates:
                  pheromone = pow(self.tau[cur][v], alpha)
                  visibility = pow(1.0 / (self.c[cur][v] + 1.0), beta)
                  w = pheromone * visibility
                  weight.append(w)
                  total += w
              r = random.random() * total


              acc = 0
              nextNode = candidates[-1]
              for i in range(len(candidates)):
                  acc += weight[i]
                  if acc >= r:
                      nextNode = candidates[i]
                      break
          path.append(nextNode)


          if nextNode <= self.n:
              picked[nextNode] = 1
              onboard.append(nextNode)
              load += 1


          else:
              p = nextNode - self.n
              delivered[p] = 1
              load -= 1
              onboard.remove(p)
          cur = nextNode
      return Route(path, self.calcCost(path))

   def depositPheromone(self, path, amount):
      cur = 0
      for x in path:
          self.tau[cur][x] += amount
          if self.tau[cur][x] > 10:
              self.tau[cur][x] = 10
          cur = x


      self.tau[cur][0] += amount
      if self.tau[cur][0] > 10:
          self.tau[cur][0] = 10

   def evaporatePheromone(self, rho):
      for i in range(self.N + 1):
          for j in range(self.N + 1):
              self.tau[i][j] *= (1.0 - rho)


              if self.tau[i][j] < 0.0001:
                  self.tau[i][j] = 0.0001

   def buildNearestPickupList(self):
      self.nearestPickup = [[] for _ in range(self.N + 1)]
      pickups = list(range(1, self.n + 1))
      for u in range(self.N + 1):


          self.nearestPickup[u] = pickups[:]


          self.nearestPickup[u].sort(key=lambda x: self.c[u][x])

   def solve(self):
      alpha = 1.0
      beta = 3.0
      rho = 0.25
      q0 = 0.85


      if self.n <= 100:
          iterations = 120
          ants = 50
          pickupCandidateLimit = 40


      elif self.n <= 300:
          iterations = 70
          ants = 35
          pickupCandidateLimit = 35


      elif self.n <= 600:
          iterations = 45
          ants = 25
          pickupCandidateLimit = 30


      else:
          iterations = 25
          ants = 15
          pickupCandidateLimit = 25


      Q = max(1, self.best.cost)
      for _ in range(iterations):
          iterationBest = Route([], 10 ** 18)
          for __ in range(ants):


              current = self.buildAntRoute(
                  alpha,
                  beta,
                  q0,
                  pickupCandidateLimit
              )
              if current.cost < iterationBest.cost:
                  iterationBest = current


              if current.cost < self.best.cost:
                  self.best = current


          self.evaporatePheromone(rho)
          self.depositPheromone(
              iterationBest.path,
              Q / iterationBest.cost
          )
          self.depositPheromone(
              self.best.path,
              Q / self.best.cost
          )

      return self.n, self.best.path


def solve():
   n, k = map(int, input().split())
   N = 2 * n
   c = [list(map(int, input().split())) for _ in range(N + 1)]
   n, best_route = ACO(n, k, c).solve()
   print(n)
   print(*best_route)


def main():
   t = 1
   for i in range(1, t+1):
      solve()


if __name__ == '__main__':
   main()
