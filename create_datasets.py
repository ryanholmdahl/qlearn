import csv
import random
from utils import get_war_data

start_year = 1989
end_year = 2014

indicators = get_war_data(1989,2014)

train_set = set()
test_set = set()

for country in indicators:
    train_sample = random.sample(indicators[country],int(len(indicators[country])*0.7))
    for year in range(start_year,end_year+1):
        if year in train_sample:
            train_set.add(((country,year),indicators[country][year]))
        else:
            test_set.add(((country,year),indicators[country][year]))

