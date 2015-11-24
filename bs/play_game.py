import random, itertools
from util import HiddenDeterministicMDP
from policy import NaivePolicy#, ValueIteration

class GameState():
    # (nplayers: 3, card_counts: [2, 6, 1])
    def __init__(self, nplayers, card_counts):
        self.nplayers = nplayers
        self.hands = [] # hands, pile, knowledge all indexed by player: [[0, 1, 0], [2, 0, 0]]
        self.pile = [] # contribution per player to pile
        self.knowledge = []
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
            for card in self.pile[player]:
                self.hands[busted][card] += self.pile[player][card]
                self.pile[player][card] = 0

    # playCards(player: 3, cards_played: [0, 1, 0])
    def playCards(self,player,cards_played):
        for card, count in enumerate(cards_played):
            self.pile[player][card] += count
            self.hands[player][card] -= count # shouldn't ever break 0

    def rotate(self, list):
        list.append(list.pop(0)) # really should use a deque to avoid shifting but yeah

    def rotateCards(self): # rotating as game values progress
        for player in range(self.nplayers):
            self.rotate(self.hands[player])
            self.rotate(self.pile[player])
            if self.knowledge[player] is not None:
                self.rotate(self.knowledge[player][1])

class BSGame(HiddenDeterministicMDP):
    # (nplayers: 3, card_counts: (2, 6, 1), policies: ????)
    def __init__(self,nplayers,card_counts,policies):
        self.nplayers = nplayers
        self.card_counts = card_counts
        self.gameState = GameState(nplayers, list(card_counts))
        self.policies = policies

    def getnext(self,cur):
        return cur + 1 if cur + 1 < self.nplayers else 0

    def getHandSizes(self):
        return tuple([sum(hand) for hand in self.gameState.hands])

    def getPileSize(self):
        return sum([sum(cards_contributed) for cards_contributed in self.gameState.pile])

    # player 0, pile/hand sizes globally known
    def startState(self):
        return ("play", 0, tuple(self.gameState.hands[0]), tuple(self.gameState.pile[0]),
            self.getPileSize(), self.gameState.knowledge[0], self.getHandSizes())

    def pprint(self, state):
        print 'state:', state[0], 'player', state[1]
        print "\tplayer's hand:", state[2]
        print '\tpile knowledge:', state[3]
        print '\tpile size:', state[4]
        print '\tbust knowledge:', state[5]
        print '\tplayer hand sizes:', state[6]
        if state[0] == 'bs':
            print '\tplay to bs:', state[7]
        print '\tpossible actions:', self.actions(state)

    # Return set of actions possible from |state|.
    def actions(self, state):
        deck_range = len(self.card_counts)
        if(state[0] == "play"):
            hand = state[2]
            hand_discrete = [card for card, count in enumerate(hand) for _ in range(count)]
            cards_playable = 4 # number of cards playable at a time, should probably be defined higher up
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
        print 'action:', action
        nextState = None
        if action == "bs":
            self.resolveBust(0, state[7]) # state[7] = play being busted
            nextState = self.playAdvTurn(self.getnext(0))
        elif action == "pass":
            if state[7][0] != self.getnext(0):
                nextState = self.playAdvBS(self.getnext(0),state[7])
            else:
                nextState = self.playAdvTurn(self.getnext(0))
        else:                             # play cards
            self.gameState.playCards(0, action) # action: (0, 1, 0)
            nextState = self.playAdvBS(self.getnext(0), (0, action))
        return (nextState, 0) #need actual utility here

    def isHonest(self,cards_played):
        for count in cards_played[1:]:
            if count != 0:
                return False
        return True

    def resolveBust(self,bs_caller,last_play):
        if self.isHonest(last_play[1]):
            self.gameState.bust(bs_caller)
        else:
            self.gameState.bust(last_play[0])

    def playAdvTurn(self,current_player):
        self.gameState.rotateCards()
        state = ("play", current_player, tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes())
        self.pprint(state)
        if current_player == 0:
            return state
        action = self.policies[current_player][state]
        self.gameState.playCards(current_player,action)
        return self.playAdvBS(self.getnext(current_player), (current_player, action))

    # playAdvBS(current_player: 1, last_play: (0, (0, 1, 0)))
    def playAdvBS(self,current_player,last_play):
        state = ("bs", current_player, tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes(), last_play)
        self.pprint(state)
        if current_player == 0:
            return state
        action = self.policies[current_player][state]
        if action == "pass":
            if self.getnext(current_player) != last_play[0]:
                return self.playAdvBS(self.getnext(current_player),last_play)
            else:
                return self.playAdvTurn(current_player)
        else:
            self.resolveBust(current_player,last_play)
            return self.playAdvTurn(current_player)

    def discount(self):
        return 1

game = BSGame(2,[2,2],[]) # (nplayers, card_counts, policies)
print 'hands', game.gameState.hands
game.pprint(game.startState())
policy = NaivePolicy()
policy.solve(game)


# print 'after play 1'
# game.gameState.rotateCards()
# print 'hands', game.gameState.hands

