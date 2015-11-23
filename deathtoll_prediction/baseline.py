from utils import get_war_data

def get_baseline_acc(countries,start_year,end_year):
    correct = 0
    total = 0
    for key in countries:
        for year in countries[key]:
            total+=1
            if countries[key][year] == -1:
                correct+=1
    return (float(correct)/total,len(countries))

def get_baseline_acc_tuples(indicator_pairs):
    correct = 0
    total = 0
    for pair in indicator_pairs:
        total+=1
        if pair[1] == -1:
            correct+=1
    return (float(correct)/total,len(indicator_pairs))

baseline_acc = get_baseline_acc(get_war_data(),1989,2014)
#baseline_acc = get_baseline_acc_tuples()

print "Final accuracy: "+str(baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"