import numpy as np
import pandas as pd
import networkx as nx
import PhysicalNetwork
import constants
from PhysicalNetwork import NetworkEnvironment as network


class LightpathLayer(nx.DiGraph):

    def __init__(self, network: network):
        super(LightpathLayer, self).__init__()
        self.network = network
        self.lightpath_num = 0
        self.lightpaths = pd.DataFrame(columns=['index', 'sd', 'path', 'wavelength', 'bandwidth', 'slice_id'])


    def establish_lightpath(self, sd: tuple, bandwidth: float, slice_id: list):
        # print(path)
        shortest_path = self.network.ksp(source=sd[0], target=sd[1], k=1)
        edges = PhysicalNetwork.extract_path(shortest_path)
        wavelength = self.network.first_fit_wavelength(path=path,bandwidth=bandwidth)
        if not wavelength:
            return False
        success = True
        for edge in edges:
            success = self.network.set_wave_capacity_edge(edge=edge,
                                                          traffic=bandwidth,
                                                          wave=wavelength,
                                                          slice_index=slice_id,
                                                          state=True)
            if not success:
                return False
        self.lightpaths.loc[index] = [self.lightpath_num, sd, path, wavelength, bandwidth, slice_id]
        self.lightpath_num += 1
        return True

    def set_lightpath(self, index: int, bandwidth: int, slice_id):
        self.lightpaths.loc[index, 'bandwidth'] += bandwidth
        self.lightpaths.loc[index, 'slice_id'].append(slice_id)
        path = self.lightpaths.loc[index, 'path']
        wave = self.lightpaths.loc[index, 'wavelength']
        edges = PhysicalNetwork.extract_path(path)
        for edge in edges:
            if_success = self.network.set_wave_capacity_edge(edge=edge,
                                                             traffic=bandwidth,
                                                             wave=wave,
                                                             slice_index=slice_id,
                                                             state=True)
            if not if_success:
                return False
        return True

    def judge_lightpath(self, sd: tuple, bandwidth: int):
        lp = self.returnSD(sd=sd)
        if lp['bandwidth'] + bandwidth > 10:
            return -1
        else:
            return lp['index']

    def setSD(self, sd: tuple, bandwidth: int, slice_id: int):
        paths = self.returnSD(sd=sd)
        if paths:
            success = False
            for path in paths:
                path_id = path['index']
                success = self.set_lightpath(index=path_id, bandwidth=bandwidth, slice_id=slice_id)
                if success:
                    return True
            if not success:
                return False
        else:
            return False


    # need to be upgraded for multi possible lightpaths between sd
    def returnSD(self, sd: tuple):
        if (not self.lightpaths.loc[self.lightpaths['sd']==sd].empty):
            return self.lightpaths.loc[self.lightpaths['sd']==sd]
        else:
            return False


    def returnPath(self, path: tuple):
        if (not self.lightpaths.loc[self.lightpaths['path']==path].empty):
            return self.lightpaths.loc[self.lightpaths['path']==path]
        else:
            return False




