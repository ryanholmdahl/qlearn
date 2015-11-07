from utils import *

def learnPredictor(trainExamples, testExamples, featureExtractor, years_back, datasets):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs, where x is a (id, year) pair), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, return the weight vector (sparse feature vector) learned.
    '''
    weights = {}  # feature => weight
    numIters = 15
    for t in range(numIters):
        eta = 0.2*(numIters-t)/(numIters)
        for tuple in trainExamples:
            phi = featureExtractor(tuple[0][0],tuple[0][1],years_back,datasets)
            score = dotProduct(weights,phi)
            if score * tuple[1] < 1:
                gradient = dict()
                for f in phi:
                    gradient[f] = -phi[f] * tuple[1]
            else:
                gradient = dict()
            increment(weights, -eta, gradient)
        print "train error: "+str(evaluatePredictor(trainExamples,lambda(x) : (1 if dotProduct(featureExtractor(x), weights) >= 0 else -1)))+", test error: "+str(evaluatePredictor(testExamples,lambda(x) : (1 if dotProduct(featureExtractor(x), weights) >= 0 else -1)))
    return weights