import util, collections, random, math

class ModelBasedAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, explorationProb=1, warmStart = None):
        self.actions = actions
        self.discount = discount
        self.explorationProb = explorationProb
        self.outcomes = {} #key is (state,action), value is [newStates]
        self.transitions = {} #key is (state, action, newState) tuple, value is number of occurrences
        self.rewards = {} #key is (state, action, newState) tuple, value is reward
        self.qCache = {} #key is (state,action), value is q
        if warmStart == None:
            self.weights = collections.Counter()
        else:
            self.weights = warmStart()
        self.numIters = 0

    def getQ(self,state,action):
        if (state,action) not in self.qCache:
            print state,action
            print self.outcomes[(state,action)]
            self.qCache[(state,action)] = sum(self.transitions[(state,action,newState)]/len(self.outcomes[(state,action)])*(self.rewards[(state,action,newState)] + self.discount*max(self.getQ(newState,newAction) for newAction in self.actions(newState) if (newState,newAction) in self.outcomes)) for newState in self.outcomes[(state,action)])
        return self.qCache[(state,action)]

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.

    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max(self.getQ(state,action) for action in self.actions(state))
            #return max((self.getQ(state, action), action) for action in self.actions(state))[1]

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
        if (state,action) in self.outcomes:
            self.outcomes[(state,action)].append(newState)
        else:
            self.outcomes[(state,action)] = [newState]
        if (state,action,newState) in self.transitions:
            self.transitions[(state,action,newState)] += 1
            self.rewards[(state,action,newState)] += 1
        else:
            self.transitions[(state,action,newState)] = 1
            self.rewards[(state,action,newState)] = 1