"""
Average Outcome Sampling Method (AOS) is a variant of the Monte Carlo
Counterfactual Regret Minimization (MCCFR) method with Outcome Sampling.
At every iteration, the counterfactual regret appended to each information
set is the expected counterfactual regret across all possible hands given
the history at the moment.
"""

from itertools import combinations
from math import factorial
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
import random
import math
import copy
import sys

"""
genRewards returns the rewards each player would receive given
the plays of each.
"""
def genRewards(strategy1, strategy2):
	# Corner Case: Invalid length of strategy
	if (len(strategy1) != len(strategy2)):
		print("Invalid inputs for strategies.")
		sys.exit()

	reward1 = 0
	reward2 = 0
	treasure = len(strategy1)
	# Compute rewards given strategies 1, 2
	for i in range(len(strategy1)):
		# player 1 wins
		if strategy1[i] > strategy2[i]:
			reward1 += treasure/2
			reward2 += -treasure/2
		# player 2 wins
		elif strategy1[i] < strategy2[i]:
			reward1 += -treasure/2
			reward2 += treasure/2
		# tie
		else:
			pass
		treasure -= 1

	return reward1, reward2

"""
genInitTables initializes initial info-set markers, regret tables,
cumulative strategy tables for all Information Sets provided.
"""
def genInitTables(maxcard):
	myList = list(range(1, maxcard + 1))

	# Generate all subsets of a given list
	subsetList = []
	for i in range(len(myList) + 1):
		subsetList += list(combinations(myList, i))

	mykey = {} # (hash, info-set) pairs
	c_I = {} # information set markers
	regret = {} # regret tables
	cumstrat = {} # cumulative strategy tables
	sigma1 = {} # strategy profile of player 1
	sigma2 = {} # strategy profile of player 2
	visits = {} # number of visits of information set

	for s in subsetList:
		hashval = hash(tuple(s)) # hash value for subset s
		c_I[hashval] = 0
		mykey[hashval] = str(s)
		regret[hashval] = {}
		cumstrat[hashval] = {}
		sigma1[hashval] = {}
		sigma2[hashval] = {}
		visits[hashval] = 0
		# nested dictionary for each action in subset s
		for a in s:
			regret[hashval][a] = 0
			cumstrat[hashval][a] = 0
			sigma1[hashval][a] = 1/len(s)
			sigma2[hashval][a] = 1/len(s)	

	return mykey, c_I, regret, cumstrat, sigma1, sigma2, visits


"""
regretMatch returns the updated strategy profile after seeing
regret on a specific information set.
"""
def regretMatch(regret, action):
	# Corner Case: Null Inputs
	if (regret == None or action == None):
		print("Null inputs.")
		sys.exit()
	# Corner Case: Invalid action
	if action not in regret:
		print("Action not in Information Set.")
		sys.exit()

	# Sum only positive regrets in regret
	totalregret = sum(regret[i] for i in regret if regret[i] > 0)

	if totalregret > 0:
		if regret[action] >= 0:
			return regret[action]/totalregret
		else:
			return 0
	else:
		return 1/len(regret)

"""
sampleCase returns an alternate history based on which information loss
the player undergoes.
"""
def sampleCase(maxcard, subscheme, i):
	# Corner Case: Invalid Input
	if (subscheme == None):
		print("Null Input.")
		sys.exit()

	history = copy.deepcopy(list(subscheme))
	# Unzip history of players[]
	Q = list(zip(*history))
	Q1 = list(Q[0])
	Q2 = list(Q[1])

	# Utility of players at given prefix z[I]
	util1, util2 = genRewards(Q1, Q2)

	allactions = list(range(1, maxcard + 1))
	size = len(Q2)

	# Maximum possible histories to search
	MAXITER = nCr(maxcard, size)*math.factorial(size)**2
	iteration = 0
	while iteration <= MAXITER:
		if i == 0: # player is player 1
			random.shuffle(Q1)
			Q2 = random.sample(allactions, size)
		else: # player is player 2
			Q1 = random.sample(allactions, size)
			random.shuffle(Q2)

		# Check that utility is preserved	
		reward1, reward2 = genRewards(Q1, Q2)
		if util1 == reward1 and util2 == reward2:
			return Q1, Q2
		iteration += 1

	# Could not find alternate history
	return list(Q[0]), list(Q[1])

"""
predictHistory returns a sample terminal history given a matched
history upto point of information loss.
"""
def predictHistory(maxcard, Q1, Q2):
	# Corner Case: Invalid Input
	if Q1 == None or Q2 == None:
		print("Null Input")
		sys.exit()

	action1 = list(range(1, maxcard + 1))
	action2 = list(range(1, maxcard + 1))
	# Discard used actions for both players
	for i in range(len(Q1)):
		action1.remove(Q1[i])
		action2.remove(Q2[i])

	# Sample the suffix history
	random.shuffle(action1)
	random.shuffle(action2)

	return list(action1), list(action2)

"""
nCr(a, b) returns a choose b.
"""
def nCr(a, b):
	val = (math.factorial(a))/(math.factorial(b)*math.factorial(a - b))
	return val

"""
computePath computes the probabilibty of ending up at prefix z[I] given
strategy sigma.
"""
def computePath(maxcard, sigma, z):
    actions = list(range(1, maxcard + 1))
    prob = 1
    for i in range(len(z)):
        hashval = hash(tuple(actions))
        prob *= sigma[hashval][z[i]]
        actions.remove(z[i])

    return prob

"""
ACTUAL GOOFSPIEL SIMULATION W/ AOS ALGORITHM
"""
def runAOS(player, maxcardvalue):
	N = player
	maxcard = maxcardvalue
	iterations = 10000
	mykey, c_I, regret, cumstrat, sigma1, sigma2, visits = genInitTables(maxcard)
	regretdata = {} # keeps track of all computed regret values

	# At each iteration
	for t in range(iterations):
		print("Iteration: ", t)
		regretdata[t] = {}
		# For each player
		for i in range(N):
			# Actions available to player
			infoset = list(range(1, maxcard + 1))

			reward = maxcard
			# Sample a terminal history
			Q1 = list(range(1, maxcard + 1))
			Q2 = list(range(1, maxcard + 1))
			random.shuffle(Q1)
			random.shuffle(Q2)
			Q = [0]*2
			Q[0] = Q1
			Q[1] = Q2
			lastaction = Q[0][4] # last action taken by player 1
			utility = genRewards(Q1, Q2)
			# At each prefix history that player i plays
			for j in range(maxcard):
				# Hash value for current information set
				hashval = hash(tuple(infoset))
				visits[hashval] += 1
				# If this isn't the start of the game
				if j > 0:
					# Maximum possible histories to search
					MAXITER = nCr(maxcard, j)*math.factorial(j)**2
					iteration = 0
					# Create cumulative regret list for each action from infoset
					cumRegret = {a: [0] for a in infoset}
					if i == 0:
						regretdata[t][j] = [0]
					FACTOR = 4
					while iteration <= MAXITER/FACTOR:
						# Discard piles of both players
						subscheme = zip(Q1[:j], Q2[:j])
						# Sample a valid alternate history
						newQ1, newQ2 = sampleCase(maxcard, subscheme, i)
						nextQ1, nextQ2 = predictHistory(maxcard, newQ1, newQ2)
						newQ1 += list(nextQ1)
						newQ2 += list(nextQ2)
						newQ = [0]*2
						newQ[0] = newQ1
						newQ[1] = newQ2
						util = genRewards(newQ1, newQ2)
						
						# For each action available
						for a in infoset:
							qz = 1/(factorial(maxcard)**2)
							sigma_player = sigma1
							sigma_opponent = sigma2
							if i == 1:
								sigma_player = sigma2
								sigma_opponent = sigma1

							pi_opp = computePath(maxcard, sigma_opponent, newQ[1 - i][:j])
							W = util[i]*pi_opp/qz

							# Compute sampled counterfactual regret
							pi_full = computePath(maxcard, sigma_player, newQ[i])
							pi_player = computePath(maxcard, sigma_player, newQ[i][:j])
							if a != newQ[i][j]: # z[I]a not in z
								if pi_full != 0:
									rtilda = -W*pi_full/pi_player
								else:
									rtilda = 0
							else:
								pi_choice = computePath(maxcard, sigma_player, newQ[i][:j + 1])
								if pi_full != 0:
									rtilda = W*pi_full*((1/pi_choice) - (1/pi_player))
								else:
									rtilda = 0

							cumRegret[a] += [rtilda]
							if i == 0 and a == lastaction:
								regretdata[t][j] += [rtilda]
						iteration += 1
					# Convert cumulative regret into average regret
					aveRegret = {a: np.mean(cumRegret[a]) for a in cumRegret}

					# Record average regret I->a into our original terminal history
					for a in infoset:
						regret[hashval][a] += aveRegret[a]
						cumstrat[hashval][a] += (t - c_I[hashval])*sigma_player[hashval][a]

				else: # j == 0 (i.e. first round of game)
					# For each action available
					for a in infoset:
						qz = 1/(factorial(maxcard)**2) # sampling probability
						sigma_player = sigma1
						sigma_opponent = sigma2
						if i == 1:
							sigma_player = sigma2
							sigma_opponent = sigma1

						pi_opp = computePath(maxcard, sigma_opponent, Q[1 - i][:j])
						W = utility[i]*pi_opp/qz
	                
						# Compute sampled counterfactual regret
						pi_full = computePath(maxcard, sigma_player, Q[i])
						pi_player = computePath(maxcard, sigma_player, Q[i][:j])
						if a != Q[i][j]: # z[I]a not in z
							if pi_full != 0:
								rtilda = -W*pi_full/pi_player
							else:
								rtilda = 0
						else:
							pi_choice = computePath(maxcard, sigma_player, Q[i][:j + 1])
							if pi_full != 0:
								rtilda = W*pi_full*((1/pi_choice) - (1/pi_player))
							else:
								rtilda = 0
						
						regret[hashval][a] += rtilda
						cumstrat[hashval][a] += (t - c_I[hashval])*sigma_player[hashval][a]

				c_I[hashval] = t # update information set market

				# Update strategy profile via regret matching
				if i == 0:
					for a in infoset:
						sigma1[hashval][a] = regretMatch(regret[hashval], a)
						if sigma1[hashval][a] > 1:
							print("Invalid Sigma 1")
							sys.exit() 
				else:
					for a in infoset:
						sigma2[hashval][a] = regretMatch(regret[hashval], a)
						if sigma2[hashval][a] > 1:
							print("Invalid Sigma 2")
							sys.exit() 

				# Card actually played by player i
				discard = Q[i][j]
				infoset.remove(discard)

				reward -= 1 # flip next card

				# End of Simulation of the Player
				if reward == 0:
					break

	return mykey, sigma1, sigma2, regret, cumstrat, visits, regretdata


