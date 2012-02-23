import random
import math

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
