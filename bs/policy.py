import random, util, collections
from util import cmb

# naive policy:
#   always passes on bs opportunities
#   plays all valid/truthful cards each time if possible
#   plays some minimal number of invalid cards otherwise
class NaivePolicy(util.PolicyGenerator):
    def __init__(self,hdmdp):
        self.hsmdp = hdmdp

    def decision(self,state):
        if state[0] == 'bs':
            return 'pass'
        else: # 'play' state
            truthful = [a for a in self.hsmdp.actions(state) if a[0] > 0 and sum(a) == a[0]]
            if truthful: #we have cards to play
                return max(truthful, key = sum)
            else:
                return min(self.hsmdp.actions(state), key = sum)

class LessStupidPolicy(util.PolicyGenerator):
    def __init__(self,hdmdp):
        self.hsmdp = hdmdp

    def decision(self,state):
        if state[0] == 'bs':
            return 'bs' if random.random() < (1 / self.hsmdp.nplayers) else 'pass'
        else: # 'play' state
            truthful = [a for a in self.hsmdp.actions(state) if a[0] > 0 and sum(a) == a[0]]
            if truthful: #we have cards to play
                return max(truthful, key = sum)
            else:
                return random.choice(self.hsmdp.actions(state))

# where sketch and confidence are on a scale from 0 to 1 inclusive
class SketchyPolicy(util.PolicyGenerator):
    def __init__(self, hdmdp, sketch, confidence = 1, learn = False):
        self.hsmdp = hdmdp
        self.sketch = sketch
        self.confidence = confidence
        self.learn = learn

    def decision(self, state_tup, id = None):
        state = self.hsmdp.todict(state_tup)

        nplayers = self.hsmdp.nplayers
        if state['state'] == 'bs':
            cardsRemoved = 0
            if state['bust_know'] and state['bs_play'][0] != state['bust_know'][0]: cardsRemoved += state['bust_know'][1][0]
            cardsRemoved += state['hand'][0] + state['knowledge'][0]
            totalInCirculation = self.hsmdp.getMaxPlayable()
            if totalInCirculation < cardsRemoved + state['bs_play'][1]:
                return 'bs'
            N = sum(state['hand_sizes'])+state['pile_size'] #total number of cards
            k = totalInCirculation - cardsRemoved #number of cards the player MIGHT have
            n = state['hand_sizes'][state['bs_play'][0]] + state['bs_play'][1] #cards the player had in hand
            x = state['bs_play'][1] #number of cards played
            if (N-k)-(n-x) < 0: #if this is true, then the player had to have had these cards
                return 'pass'

            #the relative change in hand size for the BS caller if he fails
            changeForPlayer = util.changeForPlayer(state)
            #the relative change in hand size for the player if he is caught
            changeForCaller = util.changeForCaller(state)
            #hypergeometric probability that the player had x of the card
            prob = float(cmb(k,x)) * cmb(N-k,n-x) / cmb(N,n)
            #the ai takes into account the likelihood that the opponent is lying based on previous, similar moves.
            #check advLearnCall in play_game.py for details on what exactly is stored
            learnMul = 1
            if self.learn:
                #we check if this kind of play has happened before
                if ("honesty",changeForPlayer,state['bs_play'][1]) in self.hsmdp.action_history[state['bs_play'][0]]:
                    #count up all the actions
                    actionList = self.hsmdp.action_history[state['bs_play'][0]][("honesty",changeForPlayer,state['bs_play'][1])]
                    counter = collections.Counter(actionList)
                    nActions = counter["lie"] + counter["true"]
                    lieChance = counter["lie"] / nActions
                    #we modify the multiplier based on how likely they are to BS and our confidence score
                    learnMul = 1 + (lieChance-1)*min(1,(nActions)*self.confidence)
            #we decrease the likelihood of calling based on the number of players, as we can just let someone else do it
            #we increase the likelihood of calling based on how badly a loss hurts the player
            #we decrease the likelihood of calling based on how badly a loss hurts the caller
            call = random.random() / self.hsmdp.nplayers * changeForCaller / changeForPlayer * learnMul > prob
            return 'bs' if call else 'pass'
        else:
            truthful = [a for a in self.hsmdp.actions(state_tup) if a[0] > 0 and sum(a) == a[0]] #entirely honest plays
            semitruthful = [a for a in self.hsmdp.actions(state_tup) if a[0] == state['hand'][0] and a[0] > 0 and sum(a) > a[0]] #play all of the required card and more
            full_lies = [a for a in self.hsmdp.actions(state_tup) if a[0] == 0] #play none of the required card
            if not truthful and not semitruthful: #if we don't have the card, play a number of cards weighted against future plays
                weights = {}
                for action in full_lies:
                    weight = 1
                    for i in range(0,len(action),self.hsmdp.nplayers):
                        weight *= 1/(1+action[i])
                    weights[action] = weight
                return util.weightedChoice(weights)

            #if we have a play, weight against lies that use future cards and weight the truth based on sketchiness
            weights = {}
            for action in semitruthful:
                weight = 1
                for i in range(0,len(action),self.hsmdp.nplayers):
                    weight *= 1/(1+action[i])
                weights[action] = weight
            weights[max(truthful)] = 2/(1+self.sketch)
            return util.weightedChoice(weights) #exaggerate if we can and are feeling sketchy\

            #note that we do not have an option to play only some of the required card, as I can't think of a situation where we'd want to


