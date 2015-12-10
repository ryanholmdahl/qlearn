import random, itertools
from util import HiddenStateMDP
from policy import *
from copy import deepcopy

class BSGameState():
    # (nplayers: 3, card_counts: [2, 6, 1])
    def __init__(self, nplayers, card_counts, oracle=-1):
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

        if oracle != -1:
            handSize = sum(card_counts) / nplayers
            ranksForOracle = len(card_counts) / 2 #the oracle is dealt cards only from the first len(cards)/2 cards it will play
            for i in range(ranksForOracle):
                cardAtI = oracle + i * nplayers
                if cardAtI >= len(card_counts): cardAtI -= len(card_counts)
                cards = min(card_counts[cardAtI],handSize/ranksForOracle)
                self.hands[oracle][cardAtI] += cards
                card_counts[cardAtI] -= cards

        cards = [n for n, count in enumerate(card_counts) if count > 0] # card indexes w nonzero counts
        while cards:
            for player in range(nplayers):
                if oracle != -1:
                    if player == oracle: continue
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
        saved = BSGameState(self.nplayers,[])
        saved.hands = deepcopy(self.hands)
        saved.pile = deepcopy(self.pile)
        saved.knowledge = deepcopy(self.knowledge)
        saved.last_play = deepcopy(self.last_play)
        saved.rotation_offset = self.rotation_offset
        return saved

class BSGame(HiddenStateMDP):
    # (nplayers: 3, card_counts: (2, 6, 1), policies: list of state:action maps,agent_index: 0)
    def __init__(self,nplayers,card_counts,agent_index,verbose=0,oracle=False):
        self.nplayers = nplayers
        self.card_counts = card_counts
        self.oracle=oracle
        self.gameState = BSGameState(nplayers, list(card_counts), agent_index if self.oracle else -1)
        self.agent_index = agent_index
        self.policies = None
        self.verbose = verbose
        self.wins = [0 for _ in range(nplayers)]
        self.action_history = [{} for _ in range(nplayers)]

    # Returns a copy of the game state.
    def hiddenState(self):
        return self.gameState.duplicateGameState()

    # Resets the game state with the same cards and number of players.
    def restart(self):
        self.gameState = BSGameState(self.nplayers,list(self.card_counts),self.agent_index if self.oracle else -1)
        self.action_history = [{} for _ in range(self.nplayers)]

    # Returns the state for the agent's first turn.
    def startState(self):
        return self.playAdvTurn(0) #we cycle through turns until we get to the agent's first turn

    # Return set of actions legal from |state|.
    def actions(self, state):
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

    # Performs |action| from |state|, then plays all of the adversarial turns until the agent plays again.
    def succAndReward(self, state, action):
        if self.verbose: print "(agent) player:",self.agent_index,"| action:",action
        if action == "end_game": return (None,0)
        nextState = None
        if action == "bs":
            self.resolveBust(state, self.agent_index, state[6][0]) # state[6][0] = player who last played
            nextState = self.playAdvTurn(self.getnext(state[6][0]))
        elif action == "pass":
            if state[6][0] != self.getnext(self.agent_index):
                nextState = self.playAdvBS(self.getnext(self.agent_index),state[6])
            else:
                nextState = self.playAdvTurn(self.getnext(state[6][0]))
        else:                             # play cards
            self.gameState.playCards(self.agent_index, action) # action: (0, 1, 0)
            #we sum the action because the actual cards played aren't exposed
            nextState = self.playAdvBS(self.getnext(self.agent_index), (self.agent_index, sum(action)))
        utility = 0
        if nextState[0] == "someone_wins": #this is only returned when a play turn begins and a player has no cards in hand
            if self.verbose: print "Game over. Winner:", nextState[1]
            utility = 100 if nextState[1] == self.agent_index else -100
        return (nextState, utility)

    # It's a game, so points count no matter where they are earned.
    def discount(self):
        return 1

    # When a bust occurs for any player, this function is called to store the event in the action_history.
    # A tuple key of ("honesty",changeForPlayer,cardsPlayed) is used and the outcome of the call (who busted)
    # is recorded. This way, all plays an opponent makes of the same number of cards and with the same risk to
    # itself will be treated as one.
    def advLearnCall(self,caller,state_tup,action,outcome):
        state = util.todict(state_tup)
        #the relative change in hand size for the BS caller if he fails
        changeForPlayer = util.changeForPlayer(state)
        #the relative change in hand size for the player if he is caught
        player = state['bs_play'][0]
        playerKey = ("honesty",changeForPlayer,state['bs_play'][1])
        if playerKey in self.action_history[player]:
            self.action_history[player][playerKey].append(outcome)
        else:
            self.action_history[player][playerKey] = [outcome]

    # Sets our adversary policies to those given.
    def setPolicies(self,policies):
        self.policies = policies

    # Gets the index of the player after |cur|.
    def getnext(self,cur):
        return cur + 1 if cur + 1 < self.nplayers else 0

    # Returns a tuple listing the hands size of each player.
    def getHandSizes(self):
        return tuple([sum(hand) for hand in self.gameState.hands])

    # Returns the size of the pile as an integer.
    def getPileSize(self):
        return sum([sum(cards_contributed) for cards_contributed in self.gameState.pile])

    # Returns the number of cards playable for the current "at-bat" card.
    def getMaxPlayable(self):
        return self.card_counts[self.gameState.rotation_offset%len(self.card_counts)]

    # Resets the number of wins for each player.
    def resetWins(self):
        self.wins = [0 for _ in range(self.nplayers)]

    # Returns true if the last play, stored in the game state, was honest.
    def lastPlayIsHonest(self):
        for count in self.gameState.last_play[1:]:
            if count != 0:
                return False
        return True

    # Busts the proper player in a BS call.
    def resolveBust(self,state,bs_caller,last_player):
        if self.lastPlayIsHonest():
            if self.verbose: print "player",bs_caller,"takes the pile."
            self.advLearnCall(bs_caller,state,"bs","true")
            self.gameState.bust(bs_caller)
        else:
            if self.verbose: print "player",last_player,"takes the pile."
            self.advLearnCall(bs_caller,state,"bs","lie")
            self.gameState.bust(last_player)

    # Returns the winner of the game if one exists, or None otherwise.
    def getWinner(self,hands):
        for player in range(len(hands)):
            if hands[player] == 0:
                self.wins[player] += 1
                return player
        return None

    # Prints the current status of the game.
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

    # Plays the turn of |current_player|. If that player is the agent, then we return the state and wait for a command.
    # Otherwise, we play based on the player's policy and then move on to the BS round.
    def playAdvTurn(self,current_player):
        if self.gameState.turn_number > 0: # we don't want to rotate before the first turn
            self.gameState.rotateCards()
        self.gameState.turn_number+=1
        state = ("play", tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes())
        if self.verbose == 2: self.pprint(state,current_player)
        winner = self.getWinner(state[5])
        if winner != None: return ("someone_wins",winner) #if there's a winner, the agent will end the game immediately
        if current_player == self.agent_index:
            return state
        action = self.policies[current_player](state,current_player)
        if self.verbose == 1: print "player:",current_player,"| action:",sum(action)
        if self.verbose == 2: print "player:",current_player,"| action:",action
        self.gameState.playCards(current_player,action)
        return self.playAdvBS(self.getnext(current_player), (current_player, sum(action)))

    # Runs the BS round turn of |current_player|. If that player is the agent, then we return the state and wait for
    # a command. Otherwise, we call based on the player's policy and proceed accordingly.
    def playAdvBS(self,current_player,last_play):
        state = ("bs", tuple(self.gameState.hands[current_player]), tuple(self.gameState.pile[current_player]),
            self.getPileSize(), self.gameState.knowledge[current_player], self.getHandSizes(), last_play)
        if self.verbose == 2: self.pprint(state,current_player)
        if current_player == self.agent_index:
            return state
        action = self.policies[current_player](state)
        if self.verbose: print "player:",current_player,"| action:",action
        if action == "pass":
            if self.getnext(current_player) != last_play[0]:
                return self.playAdvBS(self.getnext(current_player),last_play)
            else:
                return self.playAdvTurn(self.getnext(last_play[0]))
        else:
            self.resolveBust(state,current_player,last_play[0])
            return self.playAdvTurn(self.getnext(last_play[0]))


