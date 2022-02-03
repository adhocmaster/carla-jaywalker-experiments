import math

class GapUtils:

    @staticmethod
    def sigmoid(x):
        sig = 1 / (1 + math.exp(-x))
        return sig