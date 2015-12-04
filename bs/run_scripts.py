from tests import *

sketch_list = [random.random(), random.random(), random.random()]
agent = 0
baseline(3,4,4,5000,agent=agent,sketch_list=sketch_list)
oracle(3,4,4,5000,agent=agent,sketch_list=sketch_list)
qlearning = qlearn_learn(3,4,4,agent,15000,5000,sketch_list=sketch_list)
qlearn_test(3,4,4,agent,5000,qlearning,sketch_list=sketch_list)
#allsketchy_test(3,4,4,1000)