from util import HiddenDeterministicMDP

# naive policy:
#   always passes on bs opportunities
#   plays all valid/truthful cards each time if possible
#   plays some minimal number of invalid cards otherwise
class NaivePolicy():
    def solve(self, mdp, epsilon=0.01):
        mdp.computeStates()
        print mdp.states

        # generation
        pi = {}
        for state in mdp.states:
            if state[0] == 'bs':
                pi[state] = 'pass'
            else: # 'play' state
                truthful = [a for a in mdp.actions(state) if a[0] > 0]
                if truthful:
                    pi[state] = max(truthful, key=lambda t: t[0] - sum(t[1:]))
                else:
                    pi[state] = min(mdp.actions(state), key=sum)

        # evaluation
        V = {}
        numIters = 0
        while True:
            newV = {}
            for state, action in pi:
                newstate, reward = mdp.succAndReward(state, action)
                newV[state] = reward + mdp.discount() * V.get(newstate, 0)
            numIters += 1
            if max(abs(V.get(state, 0) - newV[state]) for state in pi) < epsilon:
                V = newV
                break
            V = newV

        self.pi = pi
        self.V = V



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


