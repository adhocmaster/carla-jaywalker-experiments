import math

class GapUtils:

    @staticmethod
    def sigmoid(x):
        print("SIGMOID(X)... \n\n\n")
        print(x)
        print("\n\n\n")
        sig = 1 / (1 + math.exp(-x))
        return sig