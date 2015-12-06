import math
import random
import util
import collections
import policy
from play_game import BSGame

#All of this is untested; I'll do that next

class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2, warmStart = None):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        if warmStart == None:
            self.weights = collections.Counter()
        else:
            self.weights = warmStart()
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

    def getAction(self, state, id=None):
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
        #print self.weights
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

def snazzyWarmStart():
    weights = collections.Counter()
    weights["hasnextcard"] = 1
    weights["smallesthand"] = 1
    return weights


#("play",tuple(self.gameState.hands[0]),tuple(self.gameState.pile[0]),self.getPileSize(),self.gameState.knowledge[0],self.getHandSizes())
def snazzyFeatureExtractor(state,action):
    features = []
    identityFeature = (state,action)
    features.append((identityFeature,1))

    if state[0] == "someone_wins": return features

    nplayers = len(state[5])
    cardsRemoved = state[1][0] + state[2][0]

    # if len(state)<7: prefix = "playturn_"
    # else: prefix = "bsturn_"

    #the hand
    features.append(("cards_"+str(state[1]),1)) #indicator
    features.append(("nofcard_"+str(state[1][0]),1))
    features.append(("has_card",1 if state[1][0] > 0 else 0))
    hasCardList = []
    for card in range(len(state[1])):
        if state[1][card] == 0:
            hasCardList.append(0)
        else:
            hasCardList.append(1)
    features.append(("hascards_"+str(hasCardList),1))

    if len(state[1]) > nplayers:
        if hasCardList[nplayers] > 0:
            features.append(("hasnextcard",1))

    #the pile
    features.append(("pile_"+str(state[2]),1)) #indicator
    # features.append(("pilesize",state[3]))
    # features.append(("npileknowledge",sum(state[2])))
    hasCardList = []
    for card in range(len(state[2])):
        if state[2][card] == 0:
            hasCardList.append(0)
        else:
            hasCardList.append(1)
    features.append(("pilehascards_"+str(hasCardList),1))

    #knowledge
    if state[4] is not None:
        for i in range(5):
            features.append(("know_"+str(i),1 if state[4][0]>=i else 0))
        features.append(("knowledge_"+str(state[4]),1))
        cardsRemoved += state[4][0]
    #    features.append(("nknowledge",sum(state[4][1])))
    #    features.append(("knowledge_cur",state[4][1][0]))

    # features.append(("cardsremoved_"+str(cardsRemoved),1))

    #opponent cards
    # features.append(("opphands_"+str(state[5]),1))
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

    features.append(("handsizerank_"+str(nHandsSmaller),1))
    # features.append(("handsizerank",nHandsSmaller+1))

    #bs
    if len(state) == 7:
        features.append(("play_"+str(state[6]),1))
    #   features.append(("playispossible",1 if cardsRemoved+state[6][1] <= 3 else 0))
    #    features.append(("played_all",1 if state[6][1] == 3 else 0)) #we need to get the actual max somehow
    #    features.append(("nplayed",state[6][1]))
    #    features.append(("player_cards",state[5][state[6][0]]))
    #    features.append(("played_cards_owned",state[1][0]))
    #

    features.append(("action_"+str(action),1))
    if action != "bs" and action !="pass":
        if sum(action) == action[0]:
            features.append(("honest",1))
        else:
            features.append(("lie",1))
            features.append(("extra_cards_"+str(sum(action)-action[0]),1))
        features.append(("nplayed_action_"+str(sum(action)),1))
        features.append(("nnextcards_played_"+str(action[nplayers]),1))

    # for i in range(1,len(features)):
    #     features[i] = (prefix+features[i][0],features[i][1])
    return features

