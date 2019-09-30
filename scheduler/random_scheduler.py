# coding:utf-8 
import random

from scheduler.chunks_scheduler import ChunkScheduler

class RandomScheduler(ChunkScheduler):
    """ Random chunk scheduler"""

    def schedule(self):

        patitions = {}
        for chunks in self.chunks:
            sites_idx = [site_id
                         for site_id, is_in in enumerate(self.chunks_mapping[chunks])  #enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
                         if is_in == 1]
            source_id = random.choice(sites_idx) #从序列中随机选取一个元素
            if source_id not in patitions:
                patitions[source_id] = []
            patitions.get(source_id).append(chunks)

        return patitions
