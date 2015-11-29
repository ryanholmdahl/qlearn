import math

class HiddenDeterministicMDP:

    def hiddenState(self): raise NotImplementedError("Override me")

    def restart(self): raise NotImplementedError("Override me")
    # Return the start state.
    def startState(self): raise NotImplementedError("Override me")

    # Return set of actions possible from |state|.
    def actions(self, state): raise NotImplementedError("Override me")

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    # Mapping to notation from class:
    #   state = s, action = a, newState = s', prob = T(s, a, s'), reward = Reward(s, a, s')
    # If IsEnd(state), return the empty list.
    def succAndReward(self, state, action): raise NotImplementedError("Override me")

    def discount(self): raise NotImplementedError("Override me")

    #I've commented this out, as I'm not sure it makes sense with a hidden determinism.

    #def computeStates(self):
    #    self.restart()
    #    self.states = set()
    #    queue = []
    #    self.states.add(self.startState())
    #    queue.append(self.startState())
    #    while len(queue) > 0:
    #        state = queue.pop()
    #        for action in self.actions(state):
    #            newState, prob, reward = self.succAndReward(state, action)
    #            if newState not in self.states:
    #                self.states.add(newState)
    #                queue.append(newState)
        # print "%d states" % len(self.states)
        # print self.states

class PolicyGenerator:
    def decision(self, state): raise NotImplementedError("Override me")

class RLAlgorithm:
    # Your algorithm will be asked to produce an action given a state.
    def getAction(self, state): raise NotImplementedError("Override me")

    # We will call this function when simulating an MDP, and you should update
    # parameters.
    # If |state| is a terminal state, this function will be called with (s, a,
    # 0, None). When this function is called, it indicates that taking action
    # |action| in state |state| resulted in reward |reward| and a transition to state
    # |newState|.
    def incorporateFeedback(self, state, action, reward, newState): raise NotImplementedError("Override me")

#combinations of n bodies into groups of size r
def cmb(n,r):
    return math.factorial(n)/(math.factorial(r)*math.factorial(n-r))