import math

class ForceFunctions:
    """We implement the eqs from
    Yang, Dongfang et al. “A Social Force Based Pedestrian Motion Model Considering Multi-Pedestrian Interaction with a Vehicle.” ACM Transactions on Spatial Algorithms and Systems (TSAS) 6 (2020): 1 - 27.

    """


    #region anisotropy functions

    @staticmethod
    def anisotropySin(radAngle, coeff):
        return (coeff + (1 - coeff) * (1 + math.cos(radAngle)) / 2)

    #endregion

    #region decaying functions
    
    @staticmethod
    def expForce(distance, A, B):
        return (A * math.exp(-(distance * B)))

    #endregion
