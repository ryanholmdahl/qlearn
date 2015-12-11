import math, random

class HiddenStateMDP:

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
def cmb(n, r):
    return math.factorial(n)/(math.factorial(r)*math.factorial(n-r))

def todict(state):
    keys = ['state', 'hand', 'knowledge', 'pile_size', 'bust_know', 'hand_sizes']
    res = {key: state[i] for i, key in enumerate(keys)}
    if state[0] == 'bs':
        res['bs_play'] = state[6]
    return res

def changeForPlayer(state):
    return (float(state['hand_sizes'][state['bs_play'][0]]) + state['pile_size']) / (state['hand_sizes'][state['bs_play'][0]] + state['bs_play'][1])

def changeForCaller(state):
    return (float(sum(state['hand'])) + state['pile_size']) / (sum(state['hand']))

def changeForPlayerAction(state, action):
    return (float(sum(state['hand'])) + state['pile_size']) / (sum(state['hand']))

def changeForCallerAction(state, action, caller):
    return (float(sum(action) + state['pile_size']) / state['hand_sizes'][caller])

def weightedChoice(weights):
    total = sum(weights.values())
    r = random.uniform(0, total)
    ssf = 0
    for action in weights:
        if ssf + weights[action] >= r:
            return action
        ssf += weights[action]
    assert False, "problem with weightedChoice"