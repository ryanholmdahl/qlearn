from tests import *

#sketch_list = [random.random(), random.random(), random.random()]
#sketch_list = [0.5, 0, 0.5] #lose
#sketch_list = [0.5, 0.5, 0]
agent = 2
baseline(3,5,3,1000)
oracle(3,5,3,1000)
#qlearning = qlearn_learn(3,5,3,agent,20000,5000,explorationProb=0.8,sketch_list=sketch_list)
#mblearning = mb_learn(3,4,4,agent,1000,1000,sketch_list=sketch_list,verbose=True)
#qlearn_test(3,5,3,agent,5000,qlearning,sketch_list=[random.random(), random.random(), random.random()])
#allsketchy_test(3,5,4,1000,sketch_list=[sketch_list[0],0,sketch_list[2]])
#human_test(3,5,4,0,qlearnings = [None,qlearning,None], sketch_list=sketch_list)