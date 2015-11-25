import random, itertools
from util import HiddenDeterministicMDP
from policy import NaivePolicy#, ValueIteration
from copy import deepcopy

class GameState():
    # (nplayers: 3, card_counts: [2, 6, 1])
    def __init__(self, nplayers, card_counts):
        self.nplayers = nplayers
        self.hands = [] # hands, pile, knowledge all indexed by player: [[0, 1, 0], [2, 0, 0]]
        self.pile = [] # contribution per player to pile
        self.knowledge = []
        self.last_play = None
        self.rotation_offset = 0
        self.turn_number = 0
        for player in range(nplayers):
            self.hands.append([])
            self.pile.append([])
            self.knowledge.append(None)
            for _ in range(len(card_counts)):
                self.pile[player].append(0)
                self.hands[player].append(0)

        cards = [n for n, count in enumerate(card_counts) if count > 0] # card indexes w nonzero counts
        while cards:
            for player in range(nplayers):
                chosen_card = random.choice(cards)
                self.hands[player][chosen_card] += 1
                card_counts[chosen_card] -= 1
                if card_counts[chosen_card] == 0:
                    cards.remove(chosen_card)
                if not cards:
                    break

    # bust(busted: 3)
    def bust(self,busted):
        for player in range(self.nplayers):
            self.knowledge[player] = (busted,tuple(self.pile[player])) # updates each player's knowledge of card transfer
            for card in range(len(self.pile[player])):
                self.hands[busted][card] += self.pile[player][card]
                self.pile[player][card] = 0

    # playCards(player: 3, cards_played: [0, 1, 0])
    def playCards(self,player,cards_played):
        self.last_play = cards_played
        for card, count in enumerate(cards_played):
            self.pile[player][card] += count
            self.hands[player][card] -= count # shouldn't ever break 0

    def rotate(self, list):
        list.append(list.pop(0)) # really should use a deque to avoid shifting but yeah

    def rotateTuple(self,to_rotate):
        to_rotate_list = list(to_rotate)
        self.rotate(to_rotate_list)
        return tuple(to_rotate_list)

    def rotateCards(self): # rotating as game values progress
        for player in range(self.nplayers):
            self.rotate(self.hands[player])
            self.rotate(self.pile[player])
            if self.knowledge[player] is not None:
                self.knowledge[player] = (self.knowledge[player][0],self.rotateTuple(self.knowledge[player][1]))
        self.rotation_offset += 1

    def duplicateGameState(self):
        saved = GameState(self.nplayers,[])
        saved.hands = deepcopy(self.hands)
        saved.pile = deepcopy(self.pile)
        saved.knowledge = deepcopy(self.knowledge)
        saved.last_play = deepcopy(self.last_play)
        saved.rotation_offset = self.rotation_offset
        return saved

class BSGame(HiddenDeterministicMDP):
    # (nplayers: 3, card_counts: (2, 6, 1), policies: list of state:action maps,agent_index: 0)
    def __init__(self,nplayers,card_counts,agent_index):
        self.nplayers = nplayers
        self.card_counts = card_counts
        self.gameState = GameState(nplayers, list(card_counts))
        self.agent_index = agent_index
        self.policies = None

    def setPolicies(self,policies):
        self.policies = policies

    def restart(self):
        self.gameState = GameState(self.nplayers,list(self.card_counts))

    def getnext(self,cur):
        return cur + 1 if cur + 1 < self.nplayers else 0

    def getHandSizes(self):
        return tuple([sum(hand) for hand in self.gameState.hands])

    def getPileSize(self):
        return sum([sum(cards_contributed) for cards_contributed in self.gameState.pile])

    def getMaxPlayable(self):
        return self.card_counts[self.gameState.rotation_offset%len(self.card_counts)]

    def lastPlayIsHonest(self):
        for count in self.gameState.last_play[1:]:
            if count != 0:
                return False
        return True

    def resolveBust(self,bs_caller,last_player):
        if self.lastPlayIsHonest():
            self.gameState.bust(bs_caller)
        else:
            self.gameState.bust(last_player)

    def hiddenState(self):
        return self.gameState

    # player 0, pile/hand sizes globally known
    def startState(self):
        return self.playAdvTurn(0) #we cycle through turns until we get to the player's first turn

    def pprint(self, state, player):
        print 'state:', state[0], "| turn:", self.gameState.turn_number
        print "\tplayer's hand:", state[1], "| player:", player
        print '\tpile knowledge:', state[2]
        print '\tpile size:', state[3]
        print '\tbust knowledge:', state[4]
        print '\tplayer hand sizes:', state[5]
        if state[0] == 'bs':
            print '\tplay to bs:', state[6]
        print '\tpossible actions:', self.actions(state)

    # Return set of actions possible from |state|.
    def actions(self, state):
        if state[0] == "over": return []
        if state[0] == "someone_wins": return ["end_game"]
        deck_range = len(self.card_counts)
        if(state[0] == "play"):
            hand = state[1]
            hand_discrete = [card for card, count in enumerate(hand) for _ in range(count)]
            cards_playable = self.getMaxPlayable() # number of cards playable at a time, should probably be defined higher up
            plays = []
            for i in range(1, cards_playable + 1):
                for combo in set(itertools.combinations(hand_discrete, i)):
                    play = [0] * deck_range
                    for card in combo:
                        play[card] += 1
                    plays.append(tuple(play))
            return plays
        else:
            return ["bs","pass"] # reaction options to other player

    # Return a (newState, reward) tuple corresponding to edge
    # coming out of |state|.
    def succAndReward(self, state, action):
        print "(agent) player:",self.agent_index,"| action:",action
        nextState = None
        if action == "end_game":
            return (("over"),100 if state[1] == self.agent_index else -100)
        elif action == "bs":
            self.resolveBust(0, state[6][0]) # state[6][0] = player who last played
            nextState = self.playAdvTurn(self.getnext(state[6][0]))
        elif action == "pass":
            if state[6][0] != self.getnext(self.agent_index):
                nextState = self.playAdvBS(self.getnext(self.agent_index),state[6])
            else:
                nextState = self.playAdvTurn(self.getnext(self.agent_index))
        else:                             # play cards
            self.gameState.playCards(self.agent_index, action) # action: (0, 1, 0)
            #we sum the action because the actual cards played aren't exposed
            nextState = self.playAdvBS(self.getnext(self.agent_index), (self.agent_index, sum(action)))
        return (nextState, 0) #need actual utility here

    def playAdvTurn(self,current_player):
        if self.gameState.turn_number > 0: # we don't want to rotate before the first turn
            self.gameState.rotateCards()
        self.gameState.turn_number+=1
        state = ("play", tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes())
        self.pprint(state,current_player)
        for player in range(len(state[5])):
            if state[5][player] == 0:
                return ("someone_wins",player)
        if current_player == self.agent_index:
            return state
        action = self.policies[current_player](state)
        print "player:",current_player,"| action:",action
        self.gameState.playCards(current_player,action)
        return self.playAdvBS(self.getnext(current_player), (current_player, sum(action)))

    # playAdvBS(current_player: 1, last_play: (0, 2)); last_play[1] only exposes the number of cards played
    def playAdvBS(self,current_player,last_play):
        state = ("bs", tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes(), last_play)
        self.pprint(state,current_player)
        if current_player == self.agent_index:
            return state
        action = self.policies[current_player](state)
        print "player:",current_player,"| action:",action
        if action == "pass":
            if self.getnext(current_player) != last_play[0]:
                return self.playAdvBS(self.getnext(current_player),last_play)
            else:
                return self.playAdvTurn(current_player)
        else:
            self.resolveBust(current_player,last_play[0])
            return self.playAdvTurn(self.getnext(last_play[0]))

    def discount(self):
        return 1


#This will only work if we draw [[1,1],[1,1]]
game = BSGame(2,[2,2],0) # (nplayers, card_counts, policies)
print 'hands', game.gameState.hands
policy = NaivePolicy(game)
game.setPolicies([None,policy.decision])
startState = game.startState()
newState, reward = game.succAndReward(startState,game.actions(startState)[0])
newState, reward = game.succAndReward(newState,"bs")
newState, reward = game.succAndReward(newState,game.actions(newState)[0])
newState, reward = game.succAndReward(newState,"pass")
newState, reward = game.succAndReward(newState, "end_game")
print reward

#print 'after play 1'
#game.gameState.rotateCards()
#print 'hands', game.gameState.hands

