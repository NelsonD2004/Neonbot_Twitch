import random


class gamble:
    rngOdds = random.choice(["Win", "Lose"])

    def getRng(self):
        return self.rngOdds
