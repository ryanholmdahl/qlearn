import csv

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

    get_locations_csv('statenames.csv',32)
    get_data_csv('nostate.csv',0,20,15)
    get_data_csv('state.csv',0,24,1,12)
    clean_long_conflicts()
    indicator_data = to_indicator()
    return indicator_data