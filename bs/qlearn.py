import math
import random
import util
import collections
import policy
from play_game import BSGame

#All of this is untested; I'll do that next

class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.Counter()
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.

    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        if newState is None:
            return
        eta = self.getStepSize()
        prediction = self.getQ(state,action)
        target = reward + self.discount * max(self.getQ(newState,newAction) for newAction in self.actions(newState))
        featureMultiplier = -eta * (prediction - target)
        features = self.featureExtractor(state,action)
        for entry in features:
            if entry[0] in self.weights:
                self.weights[entry[0]] = self.weights[entry[0]] + entry[1] * featureMultiplier
            else:
                self.weights[entry[0]] = entry[1] * featureMultiplier

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

#("play",tuple(self.gameState.hands[0]),tuple(self.gameState.pile[0]),self.getPileSize(),self.gameState.knowledge[0],self.getHandSizes())
def snazzyFeatureExtractor(state,action):
    features = []
    identityFeature = (state,action)
    features.append((identityFeature,1))

    if state[0] == "someone_wins": return features

    #the hand
    # features.append(("cards_"+str(state[1]),1)) #indicator
    # features.append(("ncards",sum(state[1])))
    hasCardList = []
    for card in range(len(state[1])):
        if state[1][card] == 0:
            hasCardList.append(0)
        else:
            hasCardList.append(1)
    features.append(("hascards_"+str(hasCardList),1))

    #the pile
    features.append(("pile_"+str(state[2]),1)) #indicator
    # features.append(("pilesize",state[3]))
    features.append(("npileknowledge",sum(state[2])))
    hasCardList = []
    for card in range(len(state[2])):
        if state[2][card] == 0:
            hasCardList.append(0)
        else:
            hasCardList.append(1)
    features.append(("pilehascards_"+str(hasCardList),1))

    #knowledge
    if state[4] is not None:
        features.append(("knowledge_"+str(state[4]),1))
    #    features.append(("nknowledge",sum(state[4][1])))
        features.append(("knowledge_cur",state[4][1][0]))

    #opponent cards
    features.append(("opphands_"+str(state[5]),1))
    nHandsLarger = 0
    nHandsSmaller = 0
    nHandsSame = -1 #compensate for the one whose hand this is
    for player in range(len(state[5])):
        if state[5][player] < sum(state[1]):
            nHandsSmaller += 1
        elif state[5][player] > sum(state[1]):
            nHandsLarger += 1
        else:
            nHandsSame += 1

    features.append(("smallesthand",1 if nHandsSmaller == 0 else 0))
    # features.append(("handsizerank",nHandsSmaller+1))

    #bs
    if len(state) == 7:
        features.append(("play_"+str(state[6]),1))
    #    features.append(("nplayed",state[6][1]))
        features.append(("player_cards",state[5][state[6][0]]))
        features.append(("played_cards_owned",state[1][0]))

    return features

