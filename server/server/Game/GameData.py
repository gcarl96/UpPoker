class GameData:
    def __init__(self):
        self.numPlayers = 0
        self.dealer = -1
        self.smallBlind = -1
        self.bigBlind = -1
        self.bigBlindVal = 10
        self.currentPlayer = -1
        self.communityCards = []
        self.players = {}
        self.activePlayers = []
        self.winningMessages = []
        self.handCount = 0
        self.numSeats = 6
        for i in range(self.numSeats):
            self.players[i] = None
        self.takenSeats = []
        self.readyForDeal = True
        self.pot = 0
        self.currentBet = 0
        self.round = None


    def SetGameType(self,game_type):
        self.gameType = game_type

    def MoveAction(self):
        if self.AllAllIn():
            return
        self.currentPlayer = (self.currentPlayer + 1) % self.numSeats
        while self.players[self.currentPlayer] == None or self.players[self.currentPlayer].action in ["Fold", "All In", "Sitting Out"]:
            self.currentPlayer = (self.currentPlayer + 1) % self.numSeats

    def DealCards(self,cards):
        for card in cards:
            self.communityCards.append(card)

    def MoveRound(self):
        if self.round == "Show":
            self.round = "PreFlop"
        elif self.round == "PreFlop":
            self.round = "Flop"
        elif self.round == "Flop":
            self.round = "Turn"
        elif self.round == "Turn":
            self.round = "River"
        elif self.round == "River":
            self.round = "Showdown"

        if (self.round == "Show" or self.round == "PreFlop"):
            self.currentPlayer = self.FindNextOccupiedSeat(self.bigBlind)
        else:
            self.currentPlayer = self.FindNextOccupiedSeat(self.dealer)
        if (self.round != "Show" and self.round != "PreFlop"):
            self.currentAction = "None"
            self.currentBet = 0
        if (self.players[self.currentPlayer].action == "Fold"):
            self.MoveAction()

    def PlayerFolds(self,seat_number):
        self.activePlayers.remove(seat_number)

    def UpdatePlayer(self,seat_number, data):
        self.players[seat_number] = data

    def NewPlayer(self,player,seat_number):
        self.numPlayers += 1
        self.players[seat_number] = player
        self.takenSeats.append(seat_number)

    def PlayerLeft(self,seat_number):
        self.numPlayers -= 1
        self.players[seat_number] = None
        self.takenSeats.remove(seat_number)
        if seat_number in self.activePlayers:
            self.PlayerFolds(seat_number)
            if seat_number == self.currentPlayer:
                self.MoveAction()

    def MoveDealer(self):
        self.dealer = self.FindNextOccupiedSeat(self.dealer)
        if (self.numPlayers == 2):
            self.smallBlind = self.dealer
        else:
            self.smallBlind = self.FindNextOccupiedSeat(self.dealer)
        self.bigBlind = self.FindNextOccupiedSeat(self.smallBlind)
        self.currentAction = "Bet"

    def NewHand(self):
        self.pot = 0
        if (self.gameType == "twoup"):
            self.round = "Show"
        else:
            self.round = "PreFlop"

        self.currentAction = "Bet"
        self.MoveDealer()
        self.currentPlayer = self.FindNextOccupiedSeat(self.bigBlind)
        self.communityCards = []
        self.activePlayers = []
        for seat_number, player in self.players.items():
            if player is not None:
                player.upCards = []
                player.action = "None"
                player.invested = 0
                player.result = 0
                self.activePlayers.append(seat_number)
        self.readyForDeal = False
        self.winningMessages = []
        self.handCount += 1
        self.currentBet = 0
        if self.handCount % 20 == 0:
            self.bigBlindVal += (int)(self.bigBlindVal*0.2)
        print(f"Players: {self.players}")

    def FindAvailableSeat(self):
        for i in range(self.numSeats):
            if i not in self.takenSeats:
                return i

    def FindNextOccupiedSeat(self, from_seat):
        next_seat = (from_seat + 1) % self.numSeats
        while self.players[next_seat] == None or self.players[next_seat].action in ["Fold", "All In"]:
            next_seat = (next_seat + 1) % self.numSeats
        return next_seat

    def AllAllIn(self):
        if len([p for p in self.activePlayers if not self.players[p].action == "All In"]) == 0:
            return True
        if len([p for p in self.activePlayers if not self.players[p].action == "All In"]) == 1:
            return self.players[[p for p in self.activePlayers if not self.players[p].action == "All In"][0]].betAmount == self.currentBet

    def ActivePlayers(self):
        return {seat_number: player for seat_number, player in self.players.items() if player is not None}

    def PlayersJSON(self):
        players_json = {}
        for seat_num, player in self.players.items():
            if player != None:
                players_json[seat_num] = player.toJSON()
            else:
                players_json[seat_num] = {}
        return players_json


    def toJSON(self):
        return {
            "round" : self.round,
            "dealer" : self.dealer,
            "smallBlind" : self.smallBlind,
            "bigBlind" : self.bigBlind,
            "currentPlayer" : self.currentPlayer,
            "communityCards" : self.communityCards,
            "players" : self.PlayersJSON(),
            "pot" : self.pot,
            "numSeats" : self.numSeats,
            "currentBet" : self.currentBet,
            "winningMessages" : self.winningMessages,
            "readyToDeal" : self.readyForDeal
        }

