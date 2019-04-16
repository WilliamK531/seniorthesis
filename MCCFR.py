"""
Monte Carlo CFR w/ Optimistic Averaging
"""

from itertools import combinations
from random import shuffle
from math import factorial
from Goofspiel import Goofspiel
import sys

"""
sampleScheme returns random order of moves predetermined
for both player 1 and 2 and the outcome at terminal history.
"""
def sampleScheme(maxcard):
    Q1 = list(range(1, maxcard + 1))
    Q2 = list(range(1, maxcard + 1))
    shuffle(Q1)
    shuffle(Q2)
    Q = list(zip(Q1, Q2))
    # Simulate a round of Goofspiel given a terminal history
    game = Goofspiel(maxcard, Q1, Q2)
    utility = game.play_round()
    return Q, utility

"""
genInitTables initializes initial info-set markers, regret tables,
cumulative strategy tables for all Information Sets provided.
"""
def genInitTables(myList):
    # Generate all subsets of a given list
    subsetList = []
    # Add to subsetList all possible subsets
    for i in range(len(myList) + 1):
        tempList = list(combinations(myList, i))
        subsetList += tempList
    mykey = {} # (hash, info-set) pairs
    c_I = {} # information set markers
    regret = {} # regret tables
    cumstrat = {} # cumulative strategy tables
    sigma1 = {} # strategy profile of player 1
    sigma2 = {} # strategy profile of player 2
    visits = {} # boolean table for visiting infosets

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
regret on a specific information set
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
        if regret[action] > 0:
            return regret[action]/totalregret
        else:
            return 0
    else:
        return 1/len(regret)

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
ACTUAL GOOFSPIEL SIMULATION W/ MCCFR ALGORITHM
"""
def runMCCFR(player, maxcardvalue):
    N = player
    maxcard = maxcardvalue
    iterations = 100000
    myList = list(range(1, maxcard + 1))
    mykey, c_I, regret, cumstrat, sigma1, sigma2, visits = genInitTables(myList)

    # At every iteration
    for t in range(iterations):
        # For each player
        for i in range(N):
            # Actions available to player
            actions = list(range(1, maxcard + 1))
            # Sample terminal history from sampling scheme
            Qzip, utility = sampleScheme(maxcard)
            Qunzip = list(zip(*Qzip))
            Q = [0]*2
            Q[0] = list(Qunzip[0])
            Q[1] = list(Qunzip[1])

            # At each prefix history that player i plays
            reward = maxcard
            for j in range(maxcard):
                # Hash value for current Information Set
                hashval = hash(tuple(actions))
                visits[hashval] += 1

                # For each action available
                for a in actions:
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

                c_I[hashval] = t # update information set marker

                # Update strategy profile via regret matching
                if i == 0:
                    for a in actions:
                        sigma1[hashval][a] = regretMatch(regret[hashval], a) 
                        if sigma1[hashval][a] > 1:
                            print("Invalid Sigma 1")
                            sys.exit()
                else:
                    for a in actions:
                        sigma2[hashval][a] = regretMatch(regret[hashval], a)
                        if sigma2[hashval][a] > 1:
                            print("Invalid Sigma 2")
                            sys.exit()

                # Card actually played by player i
                discard = Q[i][j]
                actions.remove(discard)

                reward -= 1 # flip next card

                # End of Simulation of the Player
                if reward == 0:
                    break

    return mykey, sigma1, sigma2, regret, cumstrat, visits

