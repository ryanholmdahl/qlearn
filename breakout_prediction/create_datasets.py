import sys
import random
from utils import get_war_data

start_year = 1989
end_year = 2014

def get_datasets(train_set,test_set):
    indicators = get_war_data(start_year,end_year)
    #seed = random.randint(0,sys.maxint)
    #print seed
    random.seed(32)
    for country in indicators:
        train_sample = random.sample(indicators[country],int(len(indicators[country])*0.7))
        for year in range(start_year,end_year+1):
            if year in train_sample:
                train_set.add(((country,year),indicators[country][year]))
            else:
                test_set.add(((country,year),indicators[country][year]))

