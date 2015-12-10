from tests import *

# dishonesty_list = [random.random(), random.random(), random.random()]
dishonesty_list = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
nplayers = len(dishonesty_list)
num_card_values, num_cards_per_value = 5, 3
agent = 1
ntrains = 20000
ntests = 5000

baseline(nplayers, num_card_values, num_cards_per_value, ntests, agent, dishonesty_list=dishonesty_list)
oracle(nplayers, num_card_values, num_cards_per_value, ntests, agent, dishonesty_list=dishonesty_list)
qlearning = qlearn_learn(nplayers, num_card_values, num_cards_per_value, agent, ntrains, ntests, dishonesty_list=dishonesty_list, verbose=False)
#mblearning = mb_learn(3, 4, 4, agent, 1000, 1000, dishonesty_list=dishonesty_list, verbose=True)
#qlearn_test(3, 4, 4, agent, 5000, qlearning, dishonesty_list=dishonesty_list)
#allsketchy_test(3, 5, 4, 1000, dishonesty_list=[dishonesty_list[0], 0, dishonesty_list[2]])
#human_test(3, 5, 4, 0, qlearnings = [None, qlearning, None], dishonesty_list=dishonesty_list)