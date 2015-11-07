from data_util import *


acts, locs = read_actors_locations('datasets/upcd_statenames.csv')
# print acts
# print locs
rev =  reverse(locs)
# print [(key, val) for key, val in rev.iteritems() if len(val) > 1]
codes = get_gwnums()
# print codes
codes_inv = reverse(codes)




