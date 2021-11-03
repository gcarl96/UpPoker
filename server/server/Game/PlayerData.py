class PlayerData:
    def __init__(self, seat_number, username, chips):
        self.seat_number = seat_number
        self.name = username
        self.chips = chips
        self.action = "Sitting Out"
        self.betAmount = 0
        self.upCards = []
        self.cards = []
        self.invested = 0
        self.handValue = 0
        self.result = 0

    def BlindIn(self, blind):
        self.betAmount = blind
        self.chips -= blind
        self.invested += blind
        self.action = "Bet"

    def toJSON(self):
        return {
            "seat_number" : self.seat_number,
            "name" : self.name,
            "chips" : self.chips,
            "action" : self.action,
            "betAmount" : self.betAmount,
            "upCards" : self.upCards
        }
    
    def getCards(self):
        return self.cards