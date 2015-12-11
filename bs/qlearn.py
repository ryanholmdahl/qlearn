import math
import random
import util
import collections

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
        if not newState: return
        eta = self.getStepSize()
        prediction = self.getQ(state, action)
        target = reward + self.discount * max(self.getQ(newState, newAction) for newAction in self.actions(newState))
        featureMultiplier = -eta * (prediction - target)
        features = self.featureExtractor(state, action)
        for entry in features:
            self.weights[entry[0]] = self.weights.get(entry[0], 0) + entry[1] * featureMultiplier

def bsFeatureExtractor(state, action):
    identityFeature = (state, action)
    if state[0] == "someone_wins": return [((identityFeature), 1)]

    features = []

    if state[0] == 'play':
        state_status, hand, knowledge, pilesize, bust_know, handsizes = state
    else:
        state_status, hand, knowledge, pilesize, bust_know, handsizes, bs_play = state

    nplayers = len(handsizes)
    nranks = len(hand)

    #the hand
    features.append(("have_card", 1 if hand[0] > 0 else 0)) #do we have the current card at all?
    features.append(("nofcard_"+str(hand[0]), 1)) #how many of the current card do we own?
    

    nextind = nplayers if nranks > nplayers else nplayers % nranks
    features.append(('hasnextcard', 1 if hand[nextind] > 0 else 0)) # do we have the next card to play?
    features.append(("nnextcard_"+str(hand[nextind]), 1)) # how many of the next card do we own?

    #opponent cards
    nHandsLarger = 0
    nHandsSmaller = 0
    nHandsSame = -1 #compensate for the one whose hand this is
    for player in range(len(handsizes)):
        if handsizes[player] < sum(hand):
            nHandsSmaller += 1
        elif handsizes[player] > sum(hand):
            nHandsLarger += 1
        else:
            nHandsSame += 1

    features.append(("handsizerank_"+str(nHandsSmaller), 1)) #what's our relative hand size?
    #bs
    if state_status == "bs":
        features.append((action+"_nplayed_"+str(bs_play[1]), 1)) #how many did they play?
        features.append((action+"_player_"+str(bs_play[0]), 1)) #who played it?
        know_nothave = knowledge[0] + hand[0]
        if bust_know:
            if bs_play[0] != bust_know[0]:
                know_nothave += bust_know[1][0]
            else:
                features.append((action+"_know_have_"+str(bust_know[1][0]), 1)) #how many cards do we know they have?
                features.append((action+"_has_card", 1 if bust_know[1][0] > 0 else 0))
        features.append((action+"_know_nothave_"+str(know_nothave), 1)) #how many cards do we know they don't have?
        features.append((action+"_sum_know_nothave_nplayed"+str(know_nothave + bs_play[1]), 1)) #what's the sum of the number we know they don't have and the number they played?

    features.append(("action_"+str(action), 1))
    if action != "bs" and action !="pass":
        features.append(("played_all", 1 if action[0] == hand[0] else 0)) #did we play all we had?
        if sum(action) == action[0]:
            features.append(("played_all_and_only", 1 if action[0] == hand[0] else 0)) #did we play all we had and only that?
            features.append(("honest", 1))
        else:
            features.append(("lie", 1))
            features.append(("semitruthful" if action[0] > 0 else "full_lie", 1)) #did we play any of the action card?
            features.append(("forced_lie", 1 if hand[0] == 0 else 0)) #did we have to lie?
            features.append(("extra_cards_"+str(sum(action)-action[0]), 1)) #how many fib cards did we play?
        features.append(("nplayed_action_"+str(sum(action)), 1)) #how many did we play in total?

        nextCardsPlayed = sum(action[i] for i in range(nplayers, nranks, nplayers))
        features.append(("nextcard_played", 1 if nextCardsPlayed > 0 else 0))
        features.append(("nnextcards_played_"+str(nextCardsPlayed), 1)) #how many of the next card did we play?

    return features

