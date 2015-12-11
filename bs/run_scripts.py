from tests import *

# dishonesty_list = [random.random(), random.random(), random.random()]
#dishonesty_list = [0.5, 0, 0.5] #lose


# dishonesty_list = [0.1, 0.1, 0.1, 0.1]
# dishonesty_list = [0.5, 0.5, 0.5, 0.5]
# dishonesty_list = [0.75, 0.75, 0.75, 0.75]

nplayers = 4
deckrange = 6
cards_pernum = 3

print 'agent index? (0 if empty)'
try:
    agent = int(raw_input())
except ValueError: 
    agent = 0

print 'opponent dishonesty? (random if empty)'
try:
    dis = float(raw_input())
except:
    dis = random.random()
dishonesty_list = [dis] * nplayers

print 'training iterations? (20000 if empty)'
try:
    ntrain = int(raw_input())
except ValueError:
    ntrain = 20000

print 'testing iterations? (1000 if empty)'
try:
    ntest = int(raw_input())
except:
    ntest = 1000

ntrials_nonlearning = 1000
exp_prob = 0.8

baseline(nplayers, deckrange, cards_pernum, ntrials_nonlearning)
oracle(nplayers, deckrange, cards_pernum, ntrials_nonlearning)
qlearning = qlearn_learn(nplayers, deckrange, cards_pernum, agent, ntrain, ntest, explorationProb=exp_prob, dishonesty_list=dishonesty_list, verbose=False)

#mblearning = mb_learn(3, 4, 4, agent, 1000, 1000, dishonesty_list=dishonesty_list, verbose=True)
qlearn_test(nplayers, deckrange, cards_pernum, agent, ntest, qlearning=qlearning, dishonesty_list=dishonesty_list)
#allsketchy_test(3, 5, 4, 1000, dishonesty_list=[dishonesty_list[0], 0, dishonesty_list[2]])
#human_test(3, 5, 4, 0, qlearnings = [None, qlearning, None], dishonesty_list=dishonesty_list)


print 'results from agent', agent, 'opp dishonesty', dis, 'training iters', ntrain, 'testing iters', ntest









