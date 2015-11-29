import random, util, math
from util import cmb

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

#("play",player's hand,player's pile contribution,self.getPileSize(),self.gameState.knowledge[0],self.getHandSizes(),(player,cards played))
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
            cardsRemoved = 0
            if state[4] and state[6][0] != state[4][0]: cardsRemoved += state[4][1][0]
            cardsRemoved += state[1][0] + state[2][0]
            totalInCirculation = self.hdmdp.getMaxPlayable()
            if totalInCirculation < cardsRemoved + state[6][1]:
                return 'bs'
            N = sum(state[5])+state[3] #total number of cards
            k = totalInCirculation - cardsRemoved #number of cards the player MIGHT have
            n = state[5][state[6][0]] + state[6][1] #cards the player had in hand
            x = state[6][1] #number of cards played
            if (N-k)-(n-x) < 0: #if this is true, then the player had to have had these cards
                return 'pass'

            #the relative change in hand size for the BS caller if he fails
            changeForCaller = float(state[5][state[6][0]] + state[3] + state[6][1]) / (state[5][state[6][0]] + state[6][1])
            #the relative change in hand size for the player if he is caught
            changeForPlayer = float(sum(state[1]) + state[3]) / (sum(state[1]))
            #hypergeometric probability that the player had x of the card
            prob = float(cmb(k,x)) * cmb(N-k,n-x) / cmb(N,n)
            #we decrease the likelihood of calling based on the number of players, as we can just let someone else do it
            #we increase the likelihood of calling based on how badly a loss hurts the player
            #we decrease the likelihood of calling based on how badly a loss hurts the caller
            call = random.random() / self.hdmdp.nplayers * changeForCaller / changeForPlayer > prob
            return 'bs' if call else 'pass'
        else:
            truthful = [a for a in self.hdmdp.actions(state) if a[0] > 0 and sum(a) == a[0]] #entirely honest plays
            semitruthful = [a for a in self.hdmdp.actions(state) if a[0] == state[1][0] and a[0] > 0 and sum(a) > a[0]] #play all of the required card and more
            full_lies = [a for a in self.hdmdp.actions(state) if a[0] == 0] #play none of the required card
            if not truthful and not semitruthful:
                return random.choice(full_lies) #pick a lie at random if we don't have the card
            if random.random() < self.sketch and semitruthful:
                return random.choice(semitruthful) #exaggerate if we can and are feeling sketchy
            else:
                return max(truthful) #otherwise, just play all of the card

            #note that we do not have an option to play only some of the required card, as I can't think of a situation where we'd want to


