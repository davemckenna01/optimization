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

#LaGuardia airport in New York
destination='LGA'

flights={}

for line in file('schedule.txt'):
  origin, dest, depart, arrive, price = line.strip().split(',')
  flights.setdefault((origin, dest), [])

  #Add details to the list of possible flights
  flights[(origin, dest)].append((depart, arrive, int(price)))

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
