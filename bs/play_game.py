import random
from util import HiddenDeterministicMDP

class GameState():
    def __init__(self,nplayers,card_counts):
        self.nplayers = nplayers
        self.hands = []
        self.pile = []
        self.knowledge = []
        for player in range(nplayers):
            self.hands.append([])
            self.pile.append([])
            self.knowledge.append(None)
            for _ in range(len(card_counts)):
                self.pile[player].append(0)
                self.hands[player].append(0)

        while True:
            out_of_cards = False
            for player in range(nplayers):
                chosen_card = random.randint(0,len(card_counts)-1)
                while(card_counts[chosen_card] == 0):
                    chosen_card+=1
                    if chosen_card >= len(card_counts):
                        chosen_card = 0
                self.hands[player][chosen_card]+=1
                card_counts[chosen_card] -= 1
                if sum(card_counts) == 0:
                    out_of_cards = True
                    break
            if out_of_cards:
                break

    def bust(self,buster):
        for player in range(len(self.pile)):
            self.knowledge[player] = (buster,tuple(self.pile[player]))
            for card in self.pile[player]:
                self.hands[buster][card] += self.pile[player][card]
                self.pile[player][card] = 0

    def playCards(self,player,cards_played):
        for c in range(len(cards_played)):
            self.pile[player][c] += cards_played[c]

    def rotate(self,old_list):
        newHandList = []
        for i in range(1,len(old_list)):
            newHandList.append(old_list[i])
        newHandList.append(old_list[0])
        return newHandList

    def rotateCards(self):
        for player in range(self.nplayers):
            self.hands[player] = self.rotate(self.hands[player])
            self.pile[player] = self.rotate(self.pile[player])
            if self.knowledge[player] is not None:
                self.knowledge[player][1] = tuple(self.rotate(self.knowledge[player][1]))

class BSGame(HiddenDeterministicMDP):
    def __init__(self,nplayers,card_counts,policies):
        self.nplayers = nplayers
        self.card_counts = card_counts
        self.gameState = GameState(nplayers,list(card_counts))
        self.policies = policies

    def getnext(self,cur):
        if cur+1==self.nplayers:
            return 0
        return cur+1

    def getHandSizes(self):
        handSizeList = []
        for i in range(self.nplayers):
            handSizeList.append(sum(self.gameState.hands[i]))

    def getPileSize(self):
        size = 0
        for i in range(len(self.gameState.pile)):
            size+=sum(self.gameState.pile[i])
        return size

    def startState(self):
        return ("play",tuple(self.gameState.hands[0]),tuple(self.gameState.pile[0]),self.getPileSize(),self.gameState.knowledge[0],self.getHandSizes())

    # Return set of actions possible from |state|.
    def actions(self, state):
        if(state[0]=="play"):
            plays = []
            for a in range(len(self.card_counts)):
                if state[1][a] == 0: continue
                play = []
                for x in range(len(self.card_counts)):
                    play.append(0) if x!=a else play.append(1)
                if tuple(play) not in plays: plays.append(tuple(play))

                for b in range(a,len(self.card_counts)):
                    if state[1][b] == 0: continue
                    if b == a and state[1][b] == 1: continue
                    play[b] += 1
                    if tuple(play) not in plays: plays.append(tuple(play))

                    for c in range(b,len(self.card_counts)):
                        if state[1][c] == 0: continue
                        if (c == a or c == b) and state[1][c] == 1: continue
                        if c == a and c == b and state[1][c] == 2: continue
                        play[c] += 1
                        if tuple(play) not in plays: plays.append(tuple(play))

                        for d in range(c,len(self.card_counts)):
                            hits = 0
                            if d == a: hits+=1
                            if d == b: hits+=1
                            if d == c: hits+=1
                            if state[1][d] <= hits: continue
                            play[d] += 1
                            if tuple(play) not in plays: plays.append(tuple(play))
                            play[d] -= 1

                        play[c]-=1
                    play[b]-=1
            return plays
        else:
            return ["bs","pass"]

    # Return a (newState, reward) tuple corresponding to edge
    # coming out of |state|.
    def succAndReward(self, state, action):
        nextState = None
        if action == "bs":
            self.resolveBust(0,state[6])
            nextState = self.playAdvTurn(self.getnext(0))
        elif action == "pass":
            if state[6][0] != self.getnext(0):
                nextState = self.playAdvBS(self.getnext(0),state[6])
            else:
                nextState = self.playAdvTurn(self.getnext(0))
        else:
            self.gameState.playCards(0,action)
            nextState = self.playAdvBS(self.getnext(0),(0,sum(action)))
        return (nextState, 0) #need actual utility here

    def isHonest(self,cards_played):
         for i in range(1,len(cards_played)):
             if cards_played[i]!=0:
                 return False
         return True

    def resolveBust(self,bs_caller,last_play):
        if self.isHonest(last_play[1]):
            self.gameState.bust(bs_caller)
        else:
            self.gameState.bust(last_play[0])

    def playAdvTurn(self,current_player):
        self.gameState.rotateCards()
        state = ("play",tuple(self.gameState.hands[current_player]),tuple(self.gameState.pile[current_player]),self.getPileSize(),self.gameState.knowledge[current_player],self.getHandSizes())
        if current_player == 0:
            return state

        action = self.policies[current_player][state]
        self.gameState.playCards(current_player,action)
        return self.playAdvBS(self.getnext(current_player),(current_player,action))

    def playAdvBS(self,current_player,last_play):
        state = ("bs",tuple(self.gameState.hands[current_player]),tuple(self.gameState.pile[current_player]),self.getPileSize(),self.gameState.knowledge[current_player],self.getHandSizes(),last_play)
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

game = BSGame(2,[2,2],[])
print game.gameState.hands
print game.actions(game.startState())
print game.getPileSize()
game.gameState.rotateCards()
print game.gameState.hands

# # def play_game(nplayers,policies,card_counts):
#     def winner():
#         for player in range(nplayers):
#             if sum(gameState.hands[player]) == 0:
#                 return player
#         return None
#
#     def utility(player):
#         if winner() is None:
#             return 0
#         if winner() == player:
#             return float('inf')
#         return float('-inf')
#
#     def getnext(cur):
#         if cur+1==nplayers:
#             return 0
#         return cur+1
#
#     def isHonest(cards_played):
#         for i in range(1,len(cards_played)):
#             if cards_played[i]!=0:
#                 return False
#         return True
#
#
#
#     gameState = GameState(nplayers,list(card_counts))
#     print "starting hands:"+str(gameState.hands)
#     current_player = 0
#     turnState = getTurnState(current_player)
#
#     print "pile: "+str(gameState.pile)
#     while winner() is None:
#         cards_played = policies[current_player][turnState]
#         gameState.playCards(current_player,cards_played)
#
#         #bs round
#         bs_caller = getnext(current_player)
#         while bs_caller != current_player:
#             bsState = getBSState(bs_caller,current_player,len(cards_played))
#             action = policies[bs_caller][bsState]
#             if action == "call":
#                 if isHonest(cards_played):
#                     gameState.bust(bs_caller)
#                 else:
#                     gameState.bust(current_player)
#                 break
#
#         #did he win?
#         if winner() is not None:
#             utilities = []
#             for player in range(nplayers):
#                 utilities.append(utility(player))
#             return utilities
#
#         #end of turn
#         current_player = getnext(current_player)
#         turnState = getTurnState(current_player)
#
# play_game(2,[],[2,2,2,2])