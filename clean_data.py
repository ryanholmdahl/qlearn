import csv

def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def get_reader(filename):
    f = open(filename, 'rb')
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    return csv.reader(f, dialect)

def read_table(filename):
    reader = get_reader(filename)
    table = []
    first = reader.next()
    for row in reader:
        # number thing is kind of gross and creates inconsistencies (resolved later) but whatever
        row = [dat.split(', ') if not is_number(dat) else dat for dat in row]
        table += [{first[i]: rowdat for i, rowdat in enumerate(row) if rowdat}]
    return table

    
def actors_locations():
    statenames_tab = read_table('datasets/upcd_statenames.csv')
    actors = {}
    locations = {}
    for row in statenames_tab:
        actors[row['name orig fulleng'][0]] = int(row['actorid']) # should only be one item in actor name
        for i, loc in enumerate(row['location']):
            gwnos = row['gwno loc']
            if type(gwnos) is list:
                locations[loc] = int(row['gwno loc'][i])
            else:
                locations[loc] = int(gwnos)
    return actors, locations


acts, locs = actors_locations()
print acts
print locs







