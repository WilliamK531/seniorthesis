"""
runMCCFR runs the entire MCCFR algorithm on Goofspiel, cleans data, and
checks average strategy's performance in Goofspiel.
"""

from MCCFR import runMCCFR
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from Goofspiel import Goofspiel
import numpy as np
import random

N = 2
maxcard = 5
mykey, sigma1, sigma2, regret, cumstrat, visits = runMCCFR(N, maxcard)

# Normalize cumulative strategy profile --> average strategy profile
avestrat = {}
# For each information set
for hashval in cumstrat:
	avestrat[hashval] = {}
	if sum(cumstrat[hashval].values()) == 0:
		# For each action
		for action in cumstrat[hashval]:
			avestrat[hashval][action] = 1/len(cumstrat[hashval])
	else:
		# For each action
		for action in cumstrat[hashval]:
			avestrat[hashval][action] = float(cumstrat[hashval][action])/sum(cumstrat[hashval].values())

"""
SIMULATE GAME W/ AVERAGE STRATEGY OBTAINED TO OBSERVE WIN-LOSS-TIE PERCENTAGE
"""
totalgames = 10000
count = [0]*3 # number of wins for player
for itr in range(totalgames):
	actions = list(range(1, maxcard + 1))
	strategy = []
	# Select actions based on avestrat
	for i in range(maxcard):
		hashval = hash(tuple(actions))
		# Pull out option given distribution(information set)
		options = list(avestrat[hashval].keys())
		distribution = list(avestrat[hashval].values())
		choice = np.random.choice(options, size = 1, p = distribution)
		strategy += [choice]
		actions.remove(choice)
	
	opponent = list(range(1, maxcard + 1))
	random.shuffle(opponent)
	# Simulate Results Given Choices of Actions
	Goof = Goofspiel(maxcard, strategy, opponent)
	r = Goof.play_round()

	if r[0] > r[1]: # win
		count[0] += 1
	elif r[0] < r[1]: # loss
		count[1] += 1
	else: # tie
		count[2] += 1

print("Win %: ", count[0]/totalgames)
print("Loss %: ", count[1]/totalgames)
print("Tie %: ", count[2]/totalgames)

"""
WRITE RESULTS TO EXCEL FILE
"""

results_key = pd.DataFrame([mykey])
results_strategy1 = pd.DataFrame(sigma1)
results_strategy2 = pd.DataFrame(sigma2)
results_regret = pd.DataFrame(regret)
results_cum = pd.DataFrame(cumstrat)
results_ave = pd.DataFrame(avestrat)
results_visits = pd.DataFrame([visits])



file = ExcelWriter('MCCFR_Results.xlsx')
results_key.to_excel(file, 'Key Book', index = False)
results_strategy1.to_excel(file, 'Player 1 Strategies', index = False)
results_strategy2.to_excel(file, 'Player 2 Strategies', index = False)
results_regret.to_excel(file, 'Overall Regrets', index = False)
results_cum.to_excel(file, 'Cumulative Strategy', index = False)
results_ave.to_excel(file, 'Average Strategy', index = False)
results_visits.to_excel(file, 'Visits', index = False)

file.save()
print("Results Available Now")
