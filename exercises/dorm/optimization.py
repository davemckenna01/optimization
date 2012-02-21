import time
import random
import math

s = [1,4,3,2,7,3,6,3,2,4,5,3]

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

dom = [(0, 8)] * (len(people) * 2)

#LaGuardia airport in New York
destination='LGA'

flights={}

"""
for line in file('schedule.txt'):
  origin, dest, depart, arrive, price = line.strip().split(',')
  flights.setdefault((origin, dest), [])

  #Add details to the list of possible flights
  flights[(origin, dest)].append((depart, arrive, int(price)))
"""

def getminutes(t):
  x = time.strptime(t, '%H:%M')
  return x[3] * 60 + x[4]

def printschedule(r):
  for d in range(0, len(people)):
    name = people[d][0]
    origin = people[d][1]
    out = flights[(origin, destination)][r[2 * d]]
    ret = flights[(destination, origin)][r[2 * d + 1]]
    print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                                                  out[0], out[1], out[2],
                                                  ret[0], ret[1], ret[2])
#The cost fn
def schedulecost(sol):
  totalprice = 0
  latestarrival = 0
  earliestdep = 24 * 60

  #Looping through people and working with a particular flight time
  #from that person's location, and adding up "costs" to determine a
  #total "cost" for the group.
  for d in range(len(sol) / 2):
    #Get the inbound and outbound flights
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2 * d])]
    returnf = flights[(destination, origin)][int(sol[2 * d +1])]

    #Total price is the price of all outbound and return flights
    totalprice += outbound[2]
    totalprice += returnf[2]

    #Determine the latest arrival time and ealiest departure time that
    #anyone in the group has.
    if latestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])
    if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])

  #When arriving in LGA, every person must wait at the airport until the latest person's plane arrives, so they
  #can share a rental car.
  #When departing LGA, they also must arrive at the airport at the same time in the rental car, and each
  #must wait for their own flights.
  totalwait = 0
  for d in range(len(sol) / 2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2 * d])]
    returnf = flights[(destination, origin)][int(sol[2 * d +1])]
    #This is the time spent by this person waiting between when
    #their plane landed in LGA and when the latest person's plane
    #arrived
    totalwait += latestarrival - getminutes(outbound[1])
    #This is the time spent by this person waiting between when
    #they arrived at LGA (and remember they all arrive via rental 
    #car at the same time), and when their plane departs LGA
    totalwait += getminutes(returnf[0]) - earliestdep

  #Does this solution require an extra day of car rental? That'll be $50!
  if latestarrival < earliestdep: totalprice += 50

  return totalprice + totalwait

def randomoptimize(domain, costf):
  best = 999999999
  bestr = None
  for i in range(100000):
    #Create a random solution
    r = [random.randint(domain[j][0], domain[j][1])
         for j in range(len(domain))]

    #Get the cost
    cost = costf(r)

    #Compare it to the best one so far
    if cost < best:
      best = cost
      bestr = r

    return r

def hillclimb(domain, costf):
  #Create a random solution
  sol = [random.randint(domain[j][0], domain[j][1])
         for j in range(len(domain))]

  count = 0
  #Main loop
  while 1:
    count += 1
    print "----------"
    print "Try #%s" % count
    print "----------"
    print "%s, cost = %s" % (sol, costf(sol))
    print "----------"

    #Create list of neighboring solutions.
    #A "neighboring solution" is a list that is the same as
    #a list except for one of it's items is either greater or
    #less by 1
    neighbors = []
    for j in range(len(domain)):

      #One away in each direction
      if sol[j] > domain[j][0]:
        neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j+1:])
      if sol[j] < domain[j][1]:
        neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j+1:])

      print "%s len neighbors = %s" % (j + 1, len(neighbors))

    ######################################
    #The purpose of this block is to try and find a better cost
    #from among the neighbors of the current best solution
    current = costf(sol)
    best = current
    print "Current best cost = %s" % current

    for j in range(len(neighbors)):

      cost = costf(neighbors[j])
      if cost < best:
        best = cost
        oldsol = sol
        sol = neighbors[j]
        print "We found a better configuration at %s of %s:" % (j + 1, len(neighbors))
        print "new: %s, cost = %s" % (sol, best)
        print "old: %s" % oldsol

    #If there's no improvement, then we've reached the bottom of the "hill"
    if best == current:
      print "There was no improvement"
      break
    ######################################

  return sol

#The annealing method seems to be a way of determining the riskiness
#of choosing a worse solution in the hopes that it'll yield a better 
#solution ultimately. You start out very open to risk - considering
#that you've begun in an arbitrary place anyway so what's to 
#loose, right? - but as you go on you become more risk-averse. Time
#running out/temperature decreasing might have something to do
#with it too ...

#This config produces consistently low costs
#def annealingoptimize(domain, costf, T=1000000.0, cool=0.99, step=3):

#Discovery: bigger steps result in more consistently lower costs
def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=8):
  #Initialize the values randomly
  vec = [random.randint(domain[i][0], domain[i][1])
         for i in range(len(domain))]

  while T > 0.1:
    #Choose one of the indices
    i = random.randint(0, len(domain) - 1)

    #Choose a direction to change it
    dir = random.randint(-step,step)

    #Create a new list with one of the values changed
    vecb = vec[:]
    vecb[i] += dir
    if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
    elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1]

    #Calculate the current cost and the new cost
    ea = costf(vec)
    eb = costf(vecb)

    print "Temperature: %s" % T

    print "Vector A cost = %s, Vector B cost = %s" % (ea, eb)

    #Calculate the probability cutoff
    p = pow(math.e, (-eb-ea) / T)

    print "Probability cutoff = pow(math.e, (-eb-ea) / T)"
    print "= pow(%s, (%s) / %s) = %s" % (math.e, (-eb-ea), T, p)

    print "Old vector: %s, cost %s" % (vec, ea)
    print "New vector: %s, cost %s" % (vecb, eb)

    #Is it better, or does it make the probability cutoff?
    if eb < ea:
      print "New vector is BETTER"
      print "--------------------"
      vec = vecb
    else:

      rand = random.random()
      #p is simply the probability something will be as expected,
      #and to actually decide to risk trying it you need to flip a
      #coin a few times. That's what the randomness is for here. 
      #It's for ACTING on something (acting on the probability?).

      #Also, Here "Acceptable" and "Not acceptable" really means "I'm willing to
      #risk it and "I'm not willing to risk it"
      if rand < p:
        print "New vector is WORSE, but ................... ACCEPTABLE"
        vec = vecb
        print "Here's why: Random number %s is < probability cutoff %s" % (rand, p)
      else:
        print "New vector is WORSE, and NOT acceptable"
        print "Here's why: Random number %s is > probability cutoff %s" % (rand, p)
      print "--------------------"

    #Decrease the temperature
    T = T * cool

  return vec


def geneticoptimize(domain, costf, popsize=50, step=1,
                    mutprob=0.2, elite=0.2, maxiter=100):

  #Mutation Operation
  def mutate(vec):
    #this is something like 0 or 3 or 8
    i = random.randint(0,len(domain)-1)
    rand = random.random()
    if rand < 0.5 and vec[i] > domain[i][0]:
      return vec[0:i] + [vec[i] - step] + vec[i+1:]
    elif vec[i] < domain[i][1]:
      return vec[0:i] + [vec[i] + step] + vec[i+1:]
    else:
      return vec[0:i] + [vec[i] - step] + vec[i+1:]

  # Crossover Operation
  def crossover(r1,r2):
    i=random.randint(1,len(domain)-2)
    return r1[0:i]+r2[i:]

  # Build the initial population randomly
  pop=[]
  for i in range(popsize):
    vec=[random.randint(domain[i][0],domain[i][1]) 
         for i in range(len(domain))]
    pop.append(vec)

  # How many winners from each generation?
  topelite=int(elite*popsize)

  #Main loop - this is where new populations (or "generations" in the
  #genetic metaphor) are derrived from the fittest of previous ones
  for i in range(maxiter):
    #Rank the current population
    scores=[(costf(v),v) for v in pop]
    scores.sort()
    ranked=[v for (s,v) in scores]
    #########

    #Create a new population (or generation in the metaphor)
    #consisting at first of only the "fittest" elite
    pop=ranked[0:topelite]

    ###########################
    #Then we add mutated and bred forms of those "fittest" elite
    #to the new population (or generation)
    mutations=0
    breedings=0
    while len(pop)<popsize:
      if random.random()<mutprob:

        # Mutation
        mutations += 1
        c=random.randint(0,topelite)
        pop.append(mutate(ranked[c]))

      else:

        # Crossover
        breedings += 1
        c1=random.randint(0,topelite)
        c2=random.randint(0,topelite)
        pop.append(crossover(ranked[c1],ranked[c2]))
    ##########################

    #Print current best score
    print "The fittest: %s %s - mutations and breedings in this gen: m %s b %s" % (scores[0][0], scores[0][1], mutations, breedings)

  return scores[0][1]
