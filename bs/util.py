import math

class HiddenStateMDP:

    #Returns a copy of the hidden game state.
    def hiddenState(self): raise NotImplementedError("Override me")

    #Reset the hidden state.
    def restart(self): raise NotImplementedError("Override me")

    # Return the start state.
    def startState(self): raise NotImplementedError("Override me")

    # Return set of actions possible from |state|.
    def actions(self, state): raise NotImplementedError("Override me")

    # Return a (newState, reward) tuple corresponding to the action taken in the state.
    # Note that this function is nondeterministic and uses the hidden game state in addition
    # to whatever other concealed determinants the implementation uses.
    def succAndReward(self, state, action): raise NotImplementedError("Override me")

    def discount(self): raise NotImplementedError("Override me")

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