from utils import *
import create_datasets
from baseline import get_baseline_acc_tuples
import math
import decimal

years_back = 5

def learnPredictor(trainExamples, testExamples, featureExtractor, years_back, datasets, primed_weights=None):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs, where x is a (id, year) pair), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, return the weight vector (sparse feature vector) learned.
    '''
    weights = {}  # feature => weight
    if primed_weights is not None:
        weights = primed_weights
    numIters = 200
    missWeight = 10
    found_weights = dict()
    for t in range(numIters):
        eta = 0.02
        gradient = dict()
        for tuple in trainExamples:
            phi = featureExtractor(tuple[0][0],tuple[0][1],years_back,datasets)
            score = dotProduct(weights,phi)
            if score * tuple[1] < 1: #miss
                miss_x = 1
                if tuple[1] == 1:
                    miss_x = missWeight
                for f in phi:
                    len_loss = 0
                    #if f in weights:
                         #len_loss = 2 * dotProduct(weights,weights) * weights[f]
                    if f in gradient:
                        gradient[f] += -phi[f] * tuple[1] * miss_x / len(trainExamples) + len_loss
                    else:
                        gradient[f] = -phi[f] * tuple[1] * miss_x / len(trainExamples) + len_loss

            #print tuple[1],gradient
        increment(weights, -eta, gradient)
        train_error = evaluatePredictor(trainExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), weights) >= 0 else -1))
        if frozenset(weights.iteritems()) not in found_weights:
            found_weights[frozenset(weights.iteritems())] = train_error

        print "train error: "+str(train_error)+", test error: "+str(evaluatePredictor(testExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), weights) >= 0 else -1)))
        def get_predict_error(prediction,examples):
            missed_hits = 0
            total_hits = 0
            for tuple in examples:
                if tuple[1] == prediction:
                    total_hits+=1
                    if dotProduct(weights,featureExtractor(tuple[0][0],tuple[0][1],years_back,datasets)) * prediction <= 0:
                        missed_hits +=1
            return float(missed_hits)/total_hits

        print "outbreak error (train): "+str(get_predict_error(1,trainExamples)) + ", outbreak error (test): "+str(get_predict_error(1,testExamples))
        print "peace error (train): "+str(get_predict_error(-1,trainExamples)) + ", peace error (test): "+str(get_predict_error(-1,testExamples))

    #current_min = float('inf')
    #best = {}
    #for set in found_weights:
    #    if found_weights[set] <= current_min:
    #        current_min = found_weights[set]
    #        best = dict(set)
    #print "final train error: "+str(evaluatePredictor(trainExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), best) >= 0 else -1)))+", final test error: "+str(evaluatePredictor(testExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), best) >= 0 else -1)))
    #return best
    return weights

train_set = set()
test_set = set()
create_datasets.get_datasets(train_set,test_set)

#(self,name,min_year,max_year,path,name_col,year_col,data_col,relevant_features,row_requirements=None):
unemployment_dataset = Dataset("unemployment",1979,2020,"../datasets/unemployment.csv",0,1,7,[Dataset.feature_average],{2:"Rates, total"})
gdpgrowth_dataset = Dataset("gdpgrowth",1979,2020,"../datasets/gdpgrowth.csv",0,1,2,[Dataset.feature_average,Dataset.feature_linearchange])
migration_dataset = Dataset("migration",1979,2020,"../datasets/migration.csv",0,1,2,[Dataset.feature_linearchange])
inequality_dataset = Dataset("inequality",1979,2020,"../datasets/inequality.csv",1,-1,28,[Dataset.feature_average])
human_inequality_dataset = Dataset("inequality",1979,2020,"../datasets/inequality.csv",1,-1,10,[Dataset.feature_average])
hdi_dataset = Dataset("hdi",1979,2020,"../datasets/inequality.csv",1,-1,4,[Dataset.feature_average])
gender_inequality_dataset = Dataset("gender",1979,2020,"../datasets/gender_inequality.csv",1,-1,10,[Dataset.feature_average])
gdp_dataset = Dataset("gdp",1979,2020,"../datasets/gdp.csv",0,1,3,[Dataset.feature_average],{2:"Gross Domestic Product (GDP)"})
#hdi_dataset = Dataset("hdi",1979,2020,"../datasets/hdi.csv",1,-1,6,[Dataset.feature_average])

databases = [hdi_dataset,unemployment_dataset,inequality_dataset,gdpgrowth_dataset,migration_dataset,human_inequality_dataset]
#databases = [hdi_dataset]
sets = [train_set,test_set]

for indicator_set in sets:
    toRemove = []
    for entry in indicator_set:
        for database in databases:
            if not database.tuple_valid(entry[0][0],entry[0][1],years_back) and entry not in toRemove:
                toRemove.append(entry)
    for removable in toRemove:
        indicator_set.remove(removable)

baseline_acc = get_baseline_acc_tuples(train_set)
print "Baseline train error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
baseline_acc = get_baseline_acc_tuples(test_set)
print "Baseline test error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"

weights =  learnPredictor(train_set,test_set,extract_features,years_back,databases)
print weights

#num_wars = 0
#correct = 0
#for point in train_set:
#    if point[1] != 1: continue
#    num_wars+=1
#    if dotProduct(weights,extract_features(point[0][0],point[0][1],years_back,databases)) > 0:
#        correct +=1
#        print point
#print correct,num_wars,float(correct)/num_wars

baseline_acc = get_baseline_acc_tuples(train_set)
print "Baseline train error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
baseline_acc = get_baseline_acc_tuples(test_set)
print "Baseline test error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
