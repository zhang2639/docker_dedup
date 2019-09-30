
import networkx as nx
from bitarray import bitarray

from scheduler.chunks_scheduler import ChunkScheduler


class NetworkAwareScheduler(ChunkScheduler):
    """ Network-Aware chunk scheduler

    based on max flow algorithm.

    This algorithm has a running time of $O(n^2 \sqrt{m})$ for $n$ nodes and $m$ edges.
    https://github.com/networkx/networkx/blob/master/networkx/algorithms/flow/preflowpush.py
    https://en.wikipedia.org/wiki/Push-relabel_maximum_flow_algorithm

    #chunk_nodes = at max (2 ^ #sites - 1)
    #edges = sum_i_1_sites(i * C(sites, i))
    """

    def __init__(self, sites, chunks, chunks_mapping, bw, cost=None):
        super(NetworkAwareScheduler, self).__init__(sites, chunks, chunks_mapping)
        self.bw = bw
        # self.cost = cost

        self.rev_chunks_mapping = self.__class__.reverse_dict(self.chunks_mapping)

        self.extended_chunks_mapping = {
            avail_sites: (bitarray(avail_sites), len(chunks))
            for avail_sites, chunks in self.rev_chunks_mapping.iteritems()}

        self.chunks = self.extended_chunks_mapping.keys()

        self._graph = self.build_graph_without_sink()

    @staticmethod
    def reverse_dict(olddict):
        newdict = {}
        for key, val in olddict.items():
            value = val.to01()
            if value not in newdict:
                newdict[value] = list()
            newdict[value].append(key)
        return newdict


    def build_graph_without_sink(self):
        _graph = nx.DiGraph()
        for chunk in self.chunks:
            _graph.add_edge('s', chunk, capacity=self.extended_chunks_mapping[chunk][1])
        for chunk, chunk_sites in self.extended_chunks_mapping.iteritems():
            in_sites, cap = chunk_sites
            for site_id, is_in in enumerate(in_sites):
                if is_in == 1:
                    _graph.add_edge(chunk, site_id, capacity=cap)
        return _graph

    def add_capacity_to_sink_edges(self, cap):
        for site in self.sites:
            self._graph.add_edge(site, 't', capacity=cap * self.bw[site])

    # def add_capacity_to_sink_edges_with_cost(self, cap):
    #     for site in self.sites:
    #         self._graph.add_edge(site, 't', capacity=cap, weight=self.cost[site])

    def compute_flow(self):
        flow = nx.max_flow_min_cost(self._graph, 's', 't')
        total_flow = 0
        for site in self.sites:
            total_flow += flow.get(site)['t']

        total_flow = sum(flow['s'].values())
        return flow, total_flow

    def compute_min_max_capacity(self):
        low_cap, high_cap = 1, len(self.chunks_mapping.keys())
        while low_cap < high_cap:
            cap = (low_cap + high_cap) / 2
            print "cap..", cap
            self.add_capacity_to_sink_edges(cap)
            _, total_flow = self.compute_flow()
            if total_flow == len(self.chunks_mapping.keys()):
                high_cap = cap
            else:
                low_cap = cap+1
        return low_cap


    def get_chunks_partitioning(self, flow):
        pull_site = {s: list() for s in self.sites}
        for key_chunk in self.chunks:
            chunk_sites = flow[key_chunk]
            for key_site, chunk_site_flow in chunk_sites.iteritems():
                lll = self.rev_chunks_mapping[key_chunk]
                selected, remained = lll[:chunk_site_flow], lll[chunk_site_flow:]
                pull_site[key_site].extend(selected)
                self.rev_chunks_mapping[key_chunk] = remained
        return pull_site


    def solve_optimization(self):
        cap = self.compute_min_max_capacity()
        print "min max capacity:", cap
        self.add_capacity_to_sink_edges(cap)
        flow, _ = self.compute_flow()
        return self.get_chunks_partitioning(flow)

    # def solve_optimization_for_wan_cost(self):
    #     self.add_capacity_to_sink_edges_with_cost(len(self.chunks))
    #     flow, total_flow = self.compute_flow()
    #     print "Cost:", nx.cost_of_flow(self._graph, flow)
    #     return self.get_chunks_partitioning(flow)


    def schedule(self):
        return self.solve_optimization()
