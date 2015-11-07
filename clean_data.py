from data_util import *


acts, locs = read_actors_locations('datasets/upcd_statenames.csv')
# print acts
# print locs
rev =  reverse(locs)
# print [(key, val) for key, val in rev.iteritems() if len(val) > 1]
codes = get_gwnums()
# print codes
codes_inv = reverse(codes)

countries = read_undata('datasets/gdpgrowth.csv')
notincluded = []
for c in countries:
    if c not in codes_inv:
        notincluded += [c]
for c in notincluded:
    for name in codes_inv:
        if c in name:
            print c, name
        if name in c:
            print 'wow', c, name



