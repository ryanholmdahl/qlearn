from tests import *

sketch_list = [random.random(), 0, random.random()]
agent = 1
baseline(3,5,3,5000,agent=agent,sketch_list=sketch_list)
#oracle(3,4,4,5000,agent=agent,sketch_list=sketch_list)
qlearning = qlearn_learn(3,5,3,agent,15000,5000,sketch_list=sketch_list)
#mblearning = mb_learn(3,4,4,agent,1000,1000,sketch_list=sketch_list,verbose=True)
#qlearn_test(3,4,4,agent,5000,qlearning,sketch_list=sketch_list)
#allsketchy_test(3,5,4,1000,sketch_list=[sketch_list[0],0,sketch_list[2]])
#human_test(3,5,4,0,qlearnings = [None,qlearning,None], sketch_list=sketch_list)