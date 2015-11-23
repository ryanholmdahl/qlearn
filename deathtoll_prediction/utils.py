import csv
from data_util import *

def get_war_data():
    conflicts = {}

    def get_data_csv(path, conflict_id_col, loc_id_col, year_col, death_col, requirements=None):
        with open(path, 'rb') as csvfile:
            data_reader = csv.reader(csvfile)
            for row in data_reader:
                if requirements is None: requirements = {}
                if len(row) < max(conflict_id_col,loc_id_col,year_col,death_col,max(requirements))+1: continue

                if not row[conflict_id_col].replace(',','').isdigit(): continue
                if not row[loc_id_col].replace(',','').isdigit(): continue
                if not row[year_col].replace(',','').isdigit(): continue
                if not row[death_col].replace(',','').isdigit(): continue

                passes_reqs = True
                for req_col in requirements:
                    satisfy = False
                    for possibility in requirements[req_col]:
                        if row[req_col]==possibility:
                            satisfy = True
                            break
                    if not satisfy:
                        passes_reqs = False
                        break

                if not passes_reqs: continue

                death_toll = int(row[death_col])
                location_tokens = row[loc_id_col].split(',')
                locations = []
                for token in location_tokens:
                    locations.append(int(token))
                year = int(row[year_col])
                conflict_id = int(row[conflict_id_col])

                #(year,location,toll)
                if conflict_id in conflicts:
                    for location in locations:
                        if location not in conflicts[conflict_id][1]:
                            conflicts[conflict_id][1].append(location)
                    conflicts[conflict_id] = (min(year,conflicts[conflict_id][0]),conflicts[conflict_id][1],conflicts[conflict_id][2]+death_toll)
                else:
                    conflicts[conflict_id] = (year,locations,death_toll)

    def get_tuples():
        tuples = []
        for key in conflicts:
            for loc in conflicts[key][1]:
                tuples.append(((loc,conflicts[key][0]),conflicts[key][2]))
        return tuples

    get_data_csv('../datasets/upcd_deathtolls.csv',0,20,2,11,{14:["3","4"]})
    print len(conflicts)
    return get_tuples()

print len(get_war_data())

#returns the id of a given name, or -1 if not found.
codes = get_gwnums()
rev = reverse(codes)

def get_loc_id(name):
    for c in rev:
        if name in c or c in name:
            rev[name] = rev[c]
            return rev[c]
    return -1

def get_id_names(id):
    if id in codes:
        return codes[id]
    else:
        return -1

def linear_extrapolate(known_values,min_year,max_year):
    def full(values):
        for year in range(min_year,max_year+1):
            if year not in values:
                return False
        return True

    new_values = dict()
    for year in known_values:
        new_values[year] = known_values[year]
    while not full(new_values):
        add_vals = {}
        for year in new_values:
            if year+1 not in new_values and year+1 <= max_year:
                if year-1 in new_values:
                    add_vals[year+1] = new_values[year]*2 - new_values[year-1]
                else:
                    add_vals[year+1] = new_values[year]
            if year-1 not in new_values and year-1 >= min_year:
                if year+1 in new_values:
                    add_vals[year-1] = new_values[year]*2 - new_values[year+1]
                else:
                    add_vals[year-1] = new_values[year]
        for key in add_vals:
            new_values[key] = add_vals[key]
    return new_values

class Dataset():
    #requirements is a dict with column:value
    def __init__(self,name,min_year,max_year,path,name_col,year_col,data_col,relevant_features,row_requirements=None):
        with open(path, 'rb') as csvfile:
            data_reader = csv.reader(csvfile)
            values = dict()
            for row in data_reader:
                if len(row)<max(name_col,data_col,year_col)+1: continue
                id = get_loc_id(row[name_col])
                if id is -1: continue
                if id not in values: values[id] = {}
                meets_reqs = True
                if row_requirements is not None:
                    for req in row_requirements:
                        if row[req] != row_requirements[req]:
                            meets_reqs = False
                            break
                if not meets_reqs: continue
                try:
                    values[id][int(row[year_col])] = float(row[data_col])
                except:
                    print "yikes!"
                    continue

            self.name = name
            self.values = {}
            for id in values:
                #self.values[id] = values[id]
                if len(values[id])>0:
                    self.values[id] = linear_extrapolate(values[id],min_year,max_year)
            self.min_year = min_year
            self.max_year = max_year
            self.relevant_features = relevant_features

    def tuple_valid(self,id,year,years_back):
        if id not in self.values: return False
        for i in range(year-years_back,year):
            if i not in self.values[id]:
                return False
        return True

    def feature_prevyears(self,id,year,years_back,features):
        for prevyear in range(year-years_back,year):
            for i in range(1,3):
                features[self.name+"_"+str(year-prevyear)+"_exp"+str(i)] = self.values[id][prevyear]**i

    def feature_linearchange(self,id,year,years_back,features):
        if years_back < 2:
            print "feature_linearchange failed; need at least 2 years back."
            return
        for prevyear in range(year-years_back,year):
            features[self.name+"_linchange_"+str(year-prevyear)] = 1 if self.values[id][prevyear] < self.values[id][year-1] else -1

    def feature_average(self,id,year,years_back,features):
        features[self.name+"_avg"] = sum(self.values[id][prevyear] for prevyear in range(year-years_back,year))/years_back

    def add_features(self,id,year,years_back,features):
        if years_back<1:
            print "Years back must be at least one."
            return
        if year-years_back < self.min_year or year > self.max_year+1:
            print "Dataset "+self.name+" failed; year supplied was out of range."
            return
        if id not in self.values:
            print "Id "+str(id)+" not found in dataset "+self.name
            return
        for relevant_feature in self.relevant_features:
            relevant_feature(self,id,year,years_back,features)
        return

def dotProduct(d1, d2):
    """
    @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
    @param dict d2: same as d1
    @return float: the dot product between d1 and d2
    """
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

def increment(d1, scale, d2):
    """
    Implements d1 += scale * d2 for sparse vectors.
    @param dict d1: the feature vector which is mutated.
    @param float scale
    @param dict d2: a feature vector.
    """
    for f, v in d2.items():
        if f in d1:
            d1[f] += v * scale
        else:
            d1[f] = v * scale

def evaluatePredictor(examples, predictor):
    '''
    predictor: a function that takes an x and returns a predicted y.
    Given a list of examples (x, y), makes predictions based on |predict| and returns the fraction
    of misclassiied examples.
    '''
    error = 0
    for x, y in examples:
        if predictor(x) != y:
            error += 1
    return 1.0 * error / len(examples)

def extract_features(id,year,years_back,datasets):
    features = {}
    for dataset in datasets:
        dataset.add_features(id,year,years_back,features)
    return features
