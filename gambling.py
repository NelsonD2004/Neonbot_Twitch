import random


class gamble:
    rngOdds = random.choice(["Win", "Lose"])

    def getRng(self):
        print(self.rngOdds)
        return self.rngOdds
