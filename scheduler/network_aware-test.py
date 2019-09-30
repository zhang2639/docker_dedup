# https://www.topcoder.com/community/data-science/data-science-tutorials/maximum-flow-section-2/
# http://www.geeksforgeeks.org/maximum-bipartite-matching/
# https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.flow.max_flow_min_cost.html
# https://github.com/pmneila/PyMaxflow/tree/master/examples

from scheduler.network_aware_scheduler import NetworkAwareScheduler
from bitarray import bitarray

chunks_mapping_str = """
A:1000
B:1000
C:1000
D:1000
E:1000
F:1000
G:1000
H:1000
I:1000
J:1000
"""

chunks_mapping_str = """
A:1111
B:1111
C:1111
D:1111
E:1111
F:1111
G:1111
H:1111
I:1111
J:1111
"""

chunks_mapping_str = """
A:1011
B:1011
C:1010
D:1010
E:1110
F:1110
G:1010
H:1010
I:1010
J:1010
"""


chunks_mapping = {}
for chunk_info in chunks_mapping_str.split():
    c_id, idx = chunk_info.split(':')
    chunks_mapping[c_id] = bitarray(idx)

sites = range(4)
chunks = chunks_mapping.keys()

bw = [1,1,1,1]
# bw = [1,1,2,1]

cost = [3,1,4,1]
cost = [2,1,5,2]


scheduler = NetworkAwareScheduler(sites, chunks, chunks_mapping, bw, cost)
# scheduler.test(2)

pull_site = scheduler.schedule()
for s, c in pull_site.iteritems():
    print s, c
