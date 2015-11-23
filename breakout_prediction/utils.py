from data_util import *
import math

def get_war_data(start_year, end_year):
    countries = {}
    def get_locations_csv(path, loc_col):
        with open(path, 'rb') as csvfile:
            data_reader = csv.reader(csvfile)
            for row in data_reader:
                if len(row) < loc_col+1: continue
                if not row[loc_col].replace(',','').isdigit(): continue
                tokens = row[loc_col].split(',')
                for token in tokens:
                    token_int = int(token.strip())
                    if token_int not in countries:
                        countries[token_int] = {}

    def get_data_csv(path, dyad_id_col, id_col, year_col, check_col=-1):
        with open(path, 'rb') as csvfile:
            data_reader = csv.reader(csvfile)
            for row in data_reader:
                if len(row) < max(dyad_id_col,id_col,year_col,check_col)+1: continue
                if not row[id_col].replace(',','').isdigit(): continue
                tokens = row[id_col].split(',')
                for token in tokens:
                    token_int = int(token.strip())
                    if token_int not in countries:
                        countries[token_int] = {}
                    if check_col==-1 or row[check_col] == '3':
                        year_int = int(row[year_col])
                        if year_int > end_year or year_int < start_year: continue
                        if year_int in countries[token_int]: continue
                        #if year_int-1 in countries[token_int] and countries[token_int][year_int-1] == row[dyad_id_col]: continue
                        countries[token_int][year_int] = row[dyad_id_col]

    def clean_long_conflicts():
        for country in countries:
            if len(countries[country]) == 0: continue
            latest_year = max(countries[country].keys())
            earliest_year = min(countries[country].keys())
            for i in range(latest_year,earliest_year,-1):
                if i not in countries[country]: continue
                if i-1 in countries[country] and countries[country][i-1] == countries[country][i]:
                    del countries[country][i]

    def to_indicator():
        country_history = dict()
        for country in countries:
            country_history[country] = dict()
            for year in range(start_year,end_year+1):
                if year in countries[country]:
                    country_history[country][year] = 1
                else:
                    country_history[country][year] = -1
        return country_history

    get_locations_csv('../datasets/upcd_statenames.csv',32)
    get_data_csv('../datasets/upcd_nostate.csv',0,20,15)
    get_data_csv('../datasets/upcd_state.csv',0,24,1,12)
    clean_long_conflicts()
    indicator_data = to_indicator()
    return indicator_data

#returns the id of a given name, or -1 if not found.
codes = get_gwnums()
rev = reverse(codes)

print codes[20]

def get_loc_id(name):
    if len(name) == 0: return -1
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

    if len(new_values) == 1:
       known_year = 0
       for year in new_values:
           known_year = year
       for year in range(min_year,max_year+1):
           new_values[year] = new_values[known_year]


    add_vals = {}
    known_years = sorted(new_values.keys())
    for i in range(len(known_years)-1):
        lesser_year = known_years[i]
        closest_year = known_years[i+1]

        slope = (new_values[closest_year] - new_values[lesser_year])/(closest_year-lesser_year)
        for year in range(lesser_year+1, closest_year):
            add_vals[year] = new_values[lesser_year] + slope * (year-lesser_year)

        if i==0:
            for year in range(min_year,lesser_year):
                add_vals[year] = new_values[lesser_year] + slope * (year-lesser_year)

    for key in add_vals:
        new_values[key] = add_vals[key]

    final_year = known_years[len(known_years)-1]
    remaining_slope = new_values[final_year] - new_values[final_year-1]
    for year in range(final_year,max_year+1):
        new_values[year] = new_values[final_year] + remaining_slope * (year-final_year)

    #while not full(new_values):

     #   else:
     #       add_vals = {}
     #       for lesser_year in new_values:
     #           closest_year = 30000
     #           for greater_year in new_values:
     #               if greater_year > lesser_year and greater_year < closest_year:
     #                   closest_year = greater_year
     #           if closest_year == 30000:
     #               for year in range(lesser_year+1,max_year+1):
     #                   add_vals[year] = new_values[lesser_year]
     #           else:
     #               slope = (new_values[closest_year] - new_values[lesser_year])/(closest_year-lesser_year)
     #               add_vals[lesser_year+1] = new_values[lesser_year] + slope
     #               add_vals[closest_year-1] = new_values[closest_year] - slope
     #       for key in add_vals:
     #           new_values[key] = add_vals[key]

        #add_vals = {}
        #for year in new_values:
        #    if year+1 not in new_values and year+1 <= max_year:
        #        if year-1 in new_values:
        #            add_vals[year+1] = new_values[year]*2 - new_values[year-1]
        #        else:
        #            add_vals[year+1] = new_values[year]
        #    if year-1 not in new_values and year-1 >= min_year:
        #        if year+1 in new_values:
        #            add_vals[year-1] = new_values[year]*2 - new_values[year+1]
        #        else:
        #            add_vals[year-1] = new_values[year]
    return new_values

class Dataset():
    #requirements is a dict with column:value
    def __init__(self,name,min_year,max_year,path,name_col,year_col,data_col,relevant_features,row_requirements=None):
        with open(path, 'rU') as csvfile:
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
                    if year_col!=-1:
                        values[id][int(row[year_col])] = float(row[data_col])
                        #print id, int(row[year_col]), float(row[data_col])
                    else:
                        for year in range(min_year,max_year):
                            values[id][year] = float(row[data_col])
                except:
                   # print "yikes: ",row[data_col]
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
            #for id in self.values:
                #print id

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

    def feature_average_log(self,id,year,years_back,features):
        avg = sum(self.values[id][prevyear] for prevyear in range(year-years_back,year))/years_back
        features[self.name+"_avg_log"] = math.copysign(math.log(abs(avg)),avg) if avg!=0 else 0

    def feature_average(self,id,year,years_back,features):
        avg = sum(self.values[id][prevyear] for prevyear in range(year-years_back,year))/years_back
        features[self.name+"_avg_log"] = math.copysign(math.log(abs(avg)),avg) if avg!=0 else 0
        for i in range(1,3):
            features[self.name+"_avg_"+str(i)] = (avg)**i

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
        d1[f] = d1.get(f, 0) + v * scale

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
    features = {"constant":1}
    for dataset in datasets:
        dataset.add_features(id,year,years_back,features)
    return features
