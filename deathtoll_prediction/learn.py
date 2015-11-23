from utils import *
import create_datasets
#from baseline import get_baseline_acc_tuples

years_back = 2

def learnPredictor(trainExamples, testExamples, featureExtractor, years_back, datasets, primed_weights=None):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs, where x is a (id, year) pair), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, return the weight vector (sparse feature vector) learned.
    '''
    weights = {}  # feature => weight
    if primed_weights is not None:
        weights = primed_weights
    numIters = 1000
    for t in range(numIters):
        eta = 0.0000002 * (numIters-t)/numIters
        gradient = dict()
        for tuple in trainExamples:
            phi = featureExtractor(tuple[0][0],tuple[0][1],years_back,datasets)
            score = dotProduct(weights,phi)
            #print phi, score, tuple[1], score-tuple[1]
            for f in phi:
                if f in gradient:
                    gradient[f] += phi[f] * (score-tuple[1]) / len(trainExamples)
                else:
                    gradient[f] = phi[f] * (score-tuple[1]) / len(trainExamples)
        print gradient
        #print gradient, weights
        increment(weights, -eta, gradient)
        #print weights
        #print weights
        #print "train error: "+str(evaluatePredictor(trainExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), weights) >= 0 else -1)))+", test error: "+str(evaluatePredictor(testExamples,lambda(x) : (1 if dotProduct(featureExtractor(x[0],x[1],years_back,datasets), weights) >= 0 else -1)))
    return weights

train_set = set()
test_set = set()
create_datasets.get_datasets(train_set,test_set)

unemployment_dataset = Dataset("unemployment",1979,2020,"../datasets/unemployment.csv",0,1,7,[Dataset.feature_average,Dataset.feature_prevyears],{2:"Rates, total"})
gdpgrowth_dataset = Dataset("gdpgrowth",1979,2020,"../datasets/gdpgrowth.csv",0,1,2,[Dataset.feature_prevyears])
migration_dataset = Dataset("migration",1979,2020,"../datasets/migration.csv",0,1,2,[Dataset.feature_linearchange])

#databases = [unemployment_dataset,gdpgrowth_dataset,migration_dataset]
databases = [unemployment_dataset]
sets = [train_set,test_set]

for indicator_set in sets:
    toRemove = []
    for entry in indicator_set:
        for database in databases:
            if not database.tuple_valid(entry[0][0],entry[0][1],years_back) and entry not in toRemove:
                toRemove.append(entry)
    for removable in toRemove:
        indicator_set.remove(removable)

print len(train_set)
print len(test_set)

#baseline_acc = get_baseline_acc_tuples(train_set)
#print "Baseline train error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
#baseline_acc = get_baseline_acc_tuples(test_set)
#print "Baseline test error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"

print learnPredictor(train_set,test_set,extract_features,years_back,databases)

#baseline_acc = get_baseline_acc_tuples(train_set)
#print "Baseline train error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
#baseline_acc = get_baseline_acc_tuples(test_set)
#print "Baseline test error: "+str(1-baseline_acc[0])+" with "+str(baseline_acc[1])+" counted"
