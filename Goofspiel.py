"""
Goofspiel (i.e. The Game of Pure Strategy)
*** This is for 2 players ***
"""
class Goofspiel:
	# Initialize Game w/ Number of Cards and Predetermined Strategies
	def __init__(self, card_num, strat1, strat2):
		self.treasure_count = card_num
		self.treasure_pile = list(range(1, card_num + 1))
		strat1.reverse()
		strat2.reverse()
		self.player1_pile = strat1
		self.player2_pile = strat2
		self.player1_reward = 0
		self.player2_reward = 0

	# Flip over the top card in the round
	def flip_treasure(self):
		return self.treasure_pile.pop()

	# Play a single turn of game
	def play_turn(self):
		# Empty treasure pile
		if len(self.treasure_pile) == 0:
			return False
		# Current card in play
		reward = self.flip_treasure()

		# Players' card selection
		play1 = self.player1_pile.pop()
		play2 = self.player2_pile.pop()

		if play1 > play2:
			self.player1_reward += reward/2
			self.player2_reward += -reward/2
		elif play2 > play1:
			self.player1_reward += -reward/2
			self.player2_reward += reward/2
		else:
			pass
		return True

	# Play full game given two strategies
	def play_round(self):
		while self.play_turn():
			self.play_turn()

		return self.player1_reward, self.player2_reward
	
	
	

