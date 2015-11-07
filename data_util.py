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


# extracts from upcd_statenames    
def read_actors_locations(filename):
    statenames_tab = read_table(filename)
    actors = {}
    locations = {}
    for row in statenames_tab:
        actors[row['name orig'][0]] = int(row['actorid']) # should only be one item in actor name
        for i, loc in enumerate(row['location']):
            gwnos = row['gwno loc']
            locations[loc] = int(row['gwno loc'][i]) if type(gwnos) is list else int(gwnos)
    return actors, locations


def reverse(dict):
    inv = {}
    for key, val in dict.iteritems():
        inv[val] = inv.get(val, [])
        inv[val] += [key]
    lists = [val for key, val in inv.iteritems() if len(val) > 1]
    if not lists:
        inv = {key: val[0] for key, val in inv.iteritems()}
    return inv


def get_gwnums():
    f = open('datasets/gw_states.dat', 'r')
    codes = {}
    for line in f:
        line = line.split('\t')
        codes[int(line[0])] = line[2]
    return codes

















