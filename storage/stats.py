""" A helper module that is used to record and print
    some statistics about the internals of the system;
    the number of chunks, transfer time, memory size..
    for every request.
    However, I think that the design of this module is
    not modular and need a complete redesign.
"""

import time

class State():

    def __init__(self, tag):
        self.tag = tag
        self.time = time.time()


class Statistics():

    def __init__(self, backend_storage, results_file):
        self.backend_storage = backend_storage
        self.results_file = results_file
        self.backend_storage.p2p_rpc.add_callback(7, self._network_stats_callback)

        import os
        if os.path.exists(self.results_file):
            os.remove(self.results_file)

    def new_state(self, tag, net_data=True):
        s = State(tag)
        if net_data:
            self._fill_stats(s)
        self._states[tag] = s
        return s

    def start(self, image_uuid):
        self._states = {}
        self.img = image_uuid
        self.nb_chunks, self.nb_missing_chunks, self.nb_already_available_chunks = -1,-1,-1

    def _network_stats_callback(self, msg_body, sender_id):
        self.network_stats_recv = True
        self.network_stats = msg_body[0]

    def _get_network_stats(self):
        self.network_stats_recv = False
        self.backend_storage.p2p_rpc.send_message(0,[],None)
        while not self.network_stats_recv:
            time.sleep(0.1)
        return self.network_stats

    def _fill_stats(self, state):
        network_stats = self._get_network_stats()
        state.rx, state.tx = eval(network_stats)
        state.mem = self.backend_storage.dal.repo_size()

    def output_stats(self):
        pull_st, pull_nd = self._states['pull-st'], self._states['pull-nd']
        transfer_time = pull_nd.time - pull_st.time
        mem_diff = pull_nd.mem - pull_st.mem
        tx_diff = pull_nd.tx - pull_st.tx
        rx_diff = pull_nd.rx - pull_st.rx
        write_time = self._states['write-nd'].time - self._states['write-st'].time
        if 'flow-nd' in self._states:
            flow_time = self._states['flow-nd'].time - self._states['flow-st'].time
        else:
            # in case of the image is available locally
            flow_time = 0
        dal = self.backend_storage.dal

        fields = (self.backend_storage.cfg.peer_id(), self.backend_storage.schema, \
                    dal.chunk_size, dal.compressor.level, self.img, self.nb_chunks, \
                    self.nb_already_available_chunks, self.nb_missing_chunks, \
                    round(transfer_time, 2), mem_diff, self._states['nd'].mem, \
                    round(write_time, 2), rx_diff, tx_diff, round(flow_time, 2), \
                    self.backend_storage.cfg.chunk_scheduler())
        row = ','.join(["%s"] * len(fields)) % tuple(map(str, fields))

        with open(self.results_file, 'a') as f:
            f.write(row + '\n')
            f.flush()
