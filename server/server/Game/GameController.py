from .GameData import GameData
from .PlayerData import PlayerData
import random
from treys import Evaluator, Card
from itertools import combinations

class GameController:

	def __init__(self):
		# Clients maps connection to seat_number
		self.clients = {}
		self.suits = ["C","D","H","S"]
		self.values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

		self.deck = []
		self.game = GameData()
		self.evaluator = Evaluator()

	#Called externally
	def PlayerLeaves(self,client_id):
		seat_number = self.clients[client_id]
		self.game.PlayerLeft(seat_number)
		del self.clients[client_id]

	#Called externally
	def NewPlayerJoined(self, username, connection):
		chips = 300
		seat_number = self.game.FindAvailableSeat()
		self.clients[connection] = seat_number
		newPlayerData = PlayerData(seat_number,username,chips)
		self.game.NewPlayer(newPlayerData, seat_number)
		# DistributeGameData ()


	#Called externally
	def NewDeal(self,gameType):
		if self.game.readyForDeal:
			for seat_number, player in self.game.ActivePlayers().items():
				if player.chips == 0:
					self.game.PlayerLeft(seat_number)
			self.game.SetGameType(gameType)
			self.game.NewHand ()
			self.ReadyDeck ()
			self.BlindsIn ()
			self.DealCards()
			# DistributeGameData ()

	def DealCards(self):
		numCards = 2
		if (self.game.gameType == "twoup" or self.game.gameType == "omaha"):
			numCards = 4

		for seat_number, player in self.game.ActivePlayers().items():
			player.cards = []
			for j in range(numCards):
				card = self.deck.pop(0)
				player.cards.append(card)

	#Internally called by NewDeal()
	def ReadyDeck(self):
		self.deck = []
		while (len(self.deck) < len(self.clients.keys()) * 4 + 5):
			suit = random.randint(0, 3)
			value = random.randint(0, 12)
			card =  self.values[value] + self.suits[suit]
			if not card in self.deck:
				self.deck.append(card)

	#Internally called by NewDeal()
	def BlindsIn(self):
		bigBlind = -1
		smallBlind = -1
		for seat_number, player in self.game.ActivePlayers().items():
			if seat_number == self.game.bigBlind:
				player.BlindIn (self.game.bigBlindVal)
			if seat_number == self.game.smallBlind:
				player.BlindIn (self.game.bigBlindVal/2)
		self.game.pot += 15
		self.game.currentBet = self.game.bigBlindVal
		self.game.currentAction = "Bet"

	#Called externally
	def MakeMove(self,client_id, action, amount):
		player_id = self.clients[client_id]
		if (self.game.currentPlayer != player_id or self.game.round == "show"):
			return
		successfulMove = False
		player = self.game.players[player_id]
		if action == "bet":
			print("Bet made")
			if (amount + player.chips >= self.game.currentBet and amount <= player.chips) or amount == player.chips:
				self.game.pot += amount
				self.game.currentAction = "Bet"
				player.chips -= amount
				player.betAmount += amount
				player.invested += amount
				self.game.currentBet = player.betAmount
				player.action = "Bet"
				successfulMove = True
				if (player.chips == 0):
					player.action = "All In"
		elif action == "check":
			print("Check made")
			if (self.game.currentAction in ["Check", "None"] or player.betAmount == self.game.currentBet):
					player.action = "Check"
					self.game.currentAction = "Check"
					successfulMove = True
		elif action == "fold":
			print("Fold made")
			player.action = "Fold"
			successfulMove = True
			self.game.PlayerFolds(player_id)
		elif action == "call":
			print("Call made")
			if (self.game.currentAction == "Bet"):
				if self.game.currentBet > player.betAmount + player.chips:
					self.game.pot += player.chips
					player.invested += player.chips
					player.betAmount = player.betAmount + player.chips
					player.chips = 0
				else:
					self.game.pot += self.game.currentBet - player.betAmount
					player.chips -= (self.game.currentBet - player.betAmount)
					player.invested += (self.game.currentBet - player.betAmount)
					player.betAmount = self.game.currentBet
				player.action = "Call"
				successfulMove = True
				if (player.chips == 0):
					player.action = "All In"
		if (successfulMove):
			print("Successful move")
			self.game.MoveAction()
			self.CheckRound()

	#Called internally, by CheckRound() and Showdown()
	def ClearBets(self, all_players):
		for seat_number, player in self.game.ActivePlayers().items():
			if (player.action != "Fold" and player.action != "All In") or all_players:
				player.action = "None"
				player.betAmount = 0
			if player.action == "Fold":
				player.betAmount = 0

	#Called internally, by MakeMove() and PlayerShows()
	def CheckRound(self):
		print("Checking round")
		player = self.game.players[self.game.currentPlayer]
		newRound = False
		if (self.game.round == "Show"):
			if (len(player.upCards) != 0):
				newRound = True
		elif (self.game.round == "PreFlop"):
			if (player.betAmount == self.game.currentBet and (player.seat_number != self.game.bigBlind or self.game.currentBet != self.game.bigBlindVal)):
				newRound = True
		else:
			if ((player.betAmount == self.game.currentBet and self.game.currentBet != 0) or (player.action == "Check" and self.game.currentAction == "Check")):
				newRound = True

		if (len(self.game.activePlayers) == 1):
			winner = self.game.players[self.game.activePlayers[0]]
			self.game.winningMessages = [f"{winner.name} wins {self.game.pot}"]
			winner.chips += self.game.pot
			self.ClearBets (all_players=True)
			self.game.pot = 0
			self.game.readyForDeal = True

		if (self.game.AllAllIn()):
			self.DealCommunityCards(5-len(self.game.communityCards))
			self.game.round = "Showdown"
			newRound = True
		print(f"All in: {self.game.AllAllIn()}")

		if (newRound):
			if (self.game.round != "Show"):
				self.ClearBets (all_players=False)
			if not self.game.AllAllIn():
				self.game.MoveRound ()
			if (self.game.round == "Flop"):
				self.DealCommunityCards (3)
			elif (self.game.round == "Turn"):
				self.DealCommunityCards (1)
			elif (self.game.round == "River"):
				self.DealCommunityCards (1)
			elif (self.game.round == "Showdown"):
				self.Showdown()
		print("here")

	#Called internally, by CheckRound()
	def Showdown(self):
		print("Starting showdown")
		for seat_number, player in self.game.ActivePlayers().items():
			if (player.action != "Fold"):
				player.upCards = player.cards
		print("Showdown")
		self.DecideWinner ()
		print("Winner Decided")
		self.game.pot = 0
		self.ClearBets (all_players=True)
		print("Bets cleared")
		self.game.readyForDeal = True

	def DecideWinner(self):
		for seat_number, player in self.game.ActivePlayers().items():
			player.handValue = self.CalcHandValue(self.game.communityCards, player.cards)
			print(player.invested)
		print(f"Pot size: {self.game.pot}")
		pot = 0
		while len([player for _, player in self.game.ActivePlayers().items() if player.invested > 0]) > 1:
			min_stack = min([player.invested for _, player in self.game.ActivePlayers().items() if player.invested > 0])
			print(f"Min stack: {min_stack}")
			pot += min_stack * len([player for _, player in self.game.ActivePlayers().items() if player.invested > 0])

			print(f"Best hands: {[player.handValue for _, player in self.game.ActivePlayers().items()]}")
			best_hand = min([player.handValue for _, player in self.game.ActivePlayers().items() if not player.action == "Fold" and player.invested > 0])
			print(f"The best hand was: {best_hand} - {self.evaluator.class_to_string(self.evaluator.get_rank_class(best_hand))}")
			num_winners = len([player for _, player in self.game.ActivePlayers().items() if player.handValue == best_hand and not player.action == "Fold" and player.invested > 0])
			for player in [player for _, player in self.game.ActivePlayers().items() if player.handValue == best_hand and not player.action == "Fold" and player.invested > 0]:
				print(f"{player.name} is a winner of {pot / num_winners}")
				player.result += pot / num_winners
			for _, player in self.game.ActivePlayers().items():
				player.invested -= min_stack
			pot = 0

		if len([player for _, player in self.game.ActivePlayers().items() if player.invested > 0]) == 1:
			player = [player for _, player in self.game.ActivePlayers().items() if player.invested > 0][0]
			player.result += player.invested


		for _, player in self.game.ActivePlayers().items():
			print(f"{player.name} wins {player.result} with {self.evaluator.class_to_string(self.evaluator.get_rank_class(player.handValue))}")
			player.chips += player.result
			if player.result > 0:
				self.game.winningMessages.append(f"{player.name} wins {player.result} with a {self.evaluator.class_to_string(self.evaluator.get_rank_class(player.handValue))}")
			player.result = 0
			player.invested = 0

		return 0

	def CalcHandValue(self, board_cards, hand_cards):
		boardCombs = combinations(board_cards, 3)
		boardCombs = [list(comb) for comb in list(boardCombs)]

		handCombs = combinations(hand_cards, 2)
		handCombs = [list(comb) for comb in list(handCombs)]

		max_score = 8000
		best_hand = None
		for hand in handCombs:
			for board in boardCombs:
				formatted_board = [Card.new(str(card[0])+str(card[1]).lower()) for card in board]
				formatted_hand = [Card.new(str(card[0])+str(card[1]).lower()) for card in hand]
				
				handval = self.evaluator.evaluate(formatted_board, formatted_hand)
				if (handval < max_score):
					max_score = handval
					best_hand = board + hand
		
		print(f"{max_score} - {best_hand}")
		return max_score

	#Called internally, by CheckRound()
	def DealCommunityCards(self, num):
		print(f"dealing: {num}")
		for _ in range(num):
			card = self.deck.pop()
			self.game.communityCards.append(card)

	#Called externally
	def PlayerShows(self, player_id, cards):
		if (self.game.round != "Show" or self.clients[player_id] != self.game.currentPlayer or self.game.gameType != "twoup"):
			return
		self.game.players[self.clients[player_id]].upCards = cards
		self.game.MoveAction()
		self.CheckRound ()
		# DistributeGameData ()
	
