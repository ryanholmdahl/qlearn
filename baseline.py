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

baseline_acc = get_baseline_acc(get_war_data(1989,2014),1989,2014)

print "Final accuracy: "+str(baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"