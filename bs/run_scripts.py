from tests import *

#dishonesty_list = [random.random(), random.random(), random.random()]
#dishonesty_list = [0.5, 0, 0.5] #lose
#dishonesty_list = [0.5, 0.5, 0]

agent = 2
nplayers = 3
deckrange = 5
cards_pernum = 3

baseline(nplayers, deckrange, cards_pernum, 1000)
oracle(nplayers, deckrange, cards_pernum, 1000)

#qlearning = qlearn_learn(3, 5, 3, agent, 20000, 5000, explorationProb=0.8, dishonesty_list=dishonesty_list)
#mblearning = mb_learn(3, 4, 4, agent, 1000, 1000, dishonesty_list=dishonesty_list, verbose=True)
#qlearn_test(3, 5, 3, agent, 5000, qlearning, dishonesty_list=[random.random(), random.random(), random.random()])
#allsketchy_test(3, 5, 4, 1000, dishonesty_list=[dishonesty_list[0], 0, dishonesty_list[2]])
#human_test(3, 5, 4, 0, qlearnings = [None, qlearning, None], dishonesty_list=dishonesty_list)
