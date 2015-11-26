import random, util

# naive policy:
#   always passes on bs opportunities
#   plays all valid/truthful cards each time if possible
#   plays some minimal number of invalid cards otherwise
class NaivePolicy(util.PolicyGenerator):
    def __init__(self,hdmdp):
        self.hdmdp = hdmdp

    def decision(self,state):
        if state[0] == 'bs':
            return 'pass'
        else: # 'play' state
            truthful = [a for a in self.hdmdp.actions(state) if a[0] > 0 and sum(a) == a[0]]
            if truthful: #we have cards to play
                return max(truthful, key = sum)
            else:
                return min(self.hdmdp.actions(state), key = sum)

class LessStupidPolicy(util.PolicyGenerator):
    def __init__(self,hdmdp):
        self.hdmdp = hdmdp

    def decision(self,state):
        if state[0] == 'bs':
            return 'bs' if random.random() < (1 / self.hdmdp.nplayers) else 'pass'
        else: # 'play' state
            truthful = [a for a in self.hdmdp.actions(state) if a[0] > 0 and sum(a) == a[0]]
            if truthful: #we have cards to play
                return max(truthful, key = sum)
            else:
                return random.choice(self.hdmdp.actions(state))

#("play",tuple(self.gameState.hands[0]),tuple(self.gameState.pile[0]),self.getPileSize(),self.gameState.knowledge[0],self.getHandSizes())
# where sketch is on a scale from 0 to 1 inclusive
class SketchyPolicy(util.PolicyGenerator):
    def __init__(self, hdmdp, sketch):
        self.hdmdp = hdmdp
        self.sketch = sketch

    def decision(self, state):
        if self.sketch == 0:
            np = NaivePolicy(self.hdmdp)
            return np.decision(state)
        nplayers = self.hdmdp.nplayers
        if state[0] == 'bs':
            if state[4] and state[6][0] == state[4][0]: # last play is someone we have knowledge of
                if state[6][1] > state[4][1][0]: # if we don't know that that player has all the cards in question
                    return 'bs' if random.random() < self.sketch else 'pass'
            return 'bs' if random.random() < self.sketch / 2 else 'pass'
        else:
            semitruthful = [a for a in self.hdmdp.actions(state) if a[0] > 0]
            if not semitruthful:
                return min(self.hdmdp.actions(state), key=sum)
            toplay = [] # choice of hands
            for a in semitruthful:
                if sum(a) == a[0]: # adds all fully truthful hands
                    toplay += [a]
                elif random.random() < self.sketch: # adds semitruthful hands with some probability
                    toplay += [a]
            return random.choice(toplay)


# def solve(self, hdmdp, epsilon=0.01):
#     hdmdp.computeStates()
#     print hdmdp.states
#
#     # generation
#     pi = {}
#     for state in hdmdp.states:
#
#     # evaluation
#     V = {}
#     numIters = 0
#     while True:
#         newV = {}
#         for state, action in pi:
#             newstate, reward = mdp.succAndReward(state, action)
#             newV[state] = reward + mdp.discount() * V.get(newstate, 0)
#         numIters += 1
#         if max(abs(V.get(state, 0) - newV[state]) for state in pi) < epsilon:
#             V = newV
#             break
#         V = newV
#
#     self.pi = pi
#     self.V = V



# class ValueIteration():
#     def solve(self, mdp, epsilon=0.01):
#         mdp.computeStates()
#         print mdp.states


#         # policy evaluation
#         V = {} # maps state : value of state
#         numIters = 0
#         while True:
#             newV = {}
#             for state in mdp.states:
#                 newV[state] = computeV(mdp, V, state) # implement @@@@@@@@@@@@
#             numIters += 1
#             if max(abs(V[state] - newV[state]) for state in mdp.states) < epsilon:
#                 break
#             V = newV


