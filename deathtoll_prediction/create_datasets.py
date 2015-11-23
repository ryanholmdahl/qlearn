import sys
import random
from utils import get_war_data

start_year = 1989
end_year = 2014

def get_datasets(train_set,test_set):
    tuples = get_war_data()
    #seed = random.randint(0,sys.maxint)
    #print seed
    random.seed(30)
    train_sample = random.sample(tuples,int(len(tuples)*0.7))
    for tuple in tuples:
        if tuple in train_sample:
            train_set.add(tuple)
        else:
            test_set.add(tuple)

