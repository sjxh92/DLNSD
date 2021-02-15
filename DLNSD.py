import numpy as np
import matplotlib.pyplot as plt
from TrafficModel import Request
import PhysicalNetwork
from PhysicalNetwork import NetworkEnvironment as pNetwork
import networkx as nx
import constants as C
from LightpathLayer import LightpathLayer
import itertools
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler("results1.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

GAMMA_HIGH = 1
GAMMA_LOW = 0


def trafficGenerate(n, network, total_time):
    traffic_model = TrafficModel.SliceGenerator(n, network, total_time)
    slices = traffic_model.randomGenerate()
    return slices


class DLNSD(object):
    def __init__(self, pNetwork: pNetwork):
        super(DLNSD, self).__init__()
        self.pNetwork = pNetwork
        self.lightpathlayer = LightpathLayer(self.pNetwork)
        self.lightpath_num = 0
        self.slices = None

    # option 1: reuse a existing lightpath (single hop routing)
    def option1(self, sd: tuple, bandwidth: int, slice_id: int,):
        paths = self.lightpathlayer.returnSD(sd=sd)
        temp = []
        if paths:
            for path in paths:
                temp.append(path['bandwidth'])
            index = paths[temp.index(min(temp))]['index']
            success = self.lightpathlayer.set_lightpath(index=index,bandwidth=bandwidth,slice_id=slice_id)
            if success:
                return True
            else:
                return False
        else:
            return False

    # option 2: reuse multi lightpaths in one path (multi hop routing)
    def option2(self, sd: tuple, path: list, bandwidth: int, slice_id: int):
        src,dst = sd[0],sd[1]
        shortest_path = self.ksp(src,dst,1)

        # (1  2  3  4):[1,2][1,3][1,4][2,3][2,4][3,4]
        node_pairs = PhysicalNetwork.extract_path_pro(shortest_path)

        for hop in range(len(shortest_path), 1, -1):
            bandwidth = self.latency(1, hop)
            for i in itertools.combinations(shortest_path, hop):
                edges = PhysicalNetwork.extract_path(i)
                map_success = True
                for edge in edges:
                    if(not self.lightpathlayer.setSD(sd=edge,bandwidth=bandwidth,slice_id=slice_id)):
                        map_success = False
                        break
                if map_success:
                    return True
        return False

    #option 3: establish a new lightpath between sd(single hop routing)
    def option3(self, sd: tuple, bandwidth: int, slice_id: int):
        return self.lightpathlayer.establish_lightpath(sd=sd,bandwidth=bandwidth,slice_id=slice_id)


    #option4: partly reuse existing lightpath, partly establish new lightpath
    def option4(self, sd: tuple, path: list, bandwidth: int, slice_id: int, option: str):
        if option == "min_hop":
            for i in range(3, len(path)):
                for cPath in itertools.combinations(path,i):
                    edges = PhysicalNetwork.extract_path(cPath)
                    success = True
                    for edge in edges:
                        if not self.lightpathlayer.setSD(sd=edge,bandwidth=bandwidth,slice_id=slice_id):
                            if not self.lightpathlayer.establish_lightpath(sd=edge, bandwidth=bandwidth, slice_id=slice_id):
                                success = False
                                break
                    if success:
                        return True
            return False
        elif option == "min_lightpath":
            # i: lightpath to be established
            establish = 0
            for i in range(3, len(path)):
                for cPath in itertools.combinations(path, i):
                    edges = PhysicalNetwork.extract_path(cPath)
                    success = True
                    temp = 0
                    for edge in edges:
                        if self.lightpathlayer.returnSD(sd=edge):
                            temp += 1
                    if temp + 2 == i:
                        for edge in edges:
                            if not self.lightpathlayer.setSD(sd=edge,bandwidth=bandwidth,slice_id=slice_id):
                                if not self.lightpathlayer.establish_lightpath(sd=edge,bandwidth=bandwidth,slice_id=slice_id):
                                    success = False
                                    break
                        if success:
                            return True
            return False
        elif option == "min_wavelength":
            for i in range(3, len(path)):
                for cPath in itertools.combinations(path, i):
                    edges = PhysicalNetwork.extract_path(cPath)
                    success = True
                    for edge in edges:
                        if not self.lightpathlayer.setSD(sd=edge,bandwidth=bandwidth,slice_id=slice_id):
                            if not self.pNetwork.has_edge(edge[0], edge[1]):
                                success = False
                                break
                            elif not self.lightpathlayer.establish_lightpath(sd=edge,bandwidth=bandwidth,slice_id=slice_id):
                                success = False
                                break
                    if success:
                        return True
            return False

    def DLDeploy(self):

        for s in self.slices:
            src = s.src
            dst = s.dst
            slice_index = s.index
            bandwidth = s.bandwidth

    def preprocess_request(self, ):

    def set_along_path(self, existing_lp:list, path:list, bandwidth: int, slice_id: int):
        start_node = path[0]
        for p in range(1, len(path)):
            end_node = path[p]
            index = self.lightpathlayer.judge_lightpath((start_node,end_node), bandwidth)
            if index >= 0:
                self.lightpathlayer.set_lightpath(index=index, bandwidth=bandwidth, slice_id=slice_id)
            else:
                return False
        return True




    def latency(self, R, n):
        return n

    def trafficProcess(self, traffic: int):
        a = traffic // 10
        b = traffic - (a * 10)
        traffic_list = []
        if b > 0:
            traffic_list.append(b)
        for i in range(a):
            traffic_list.append(10)
        return traffic_list

    def resetSlices(self):
        for s in self.slices:
            times = np.arange(C.TOTAL_TIME)
            if not s.state.empty:
                s.state.drop(index=times, axis=0, inplace=True)



    def showRequest(self):
        for s in self.slices:
            print('|slice id: ', s.index, '|slice src: ', s.src,
                  '|slice dst: ', s.dst, '|slice traffic', s.traffic,
                  '|slice priority: ', s.priority, '|total time: ', s.t_time)
            if not s.state.empty:
                print(s.state)


    def drawRequest(self):
        x = np.arange(self.total_time)
        y = np.zeros(shape=(len(self.slices), self.total_time), dtype=np.int)
        for i in range(len(self.slices)):
            y[i] = self.slices[i].traffic
            plt.plot(x, y[i], label=self.slices[i].src)
        plt.legend()
        plt.xlabel('time')
        plt.ylabel('traffic')
        plt.show()


    def showPath(self, path: list):
        edges = self.network.extract_path(path)
        for edge in edges:
            for w in range(self.network.wave_num):
                print(self.network.get_edge_data(edge[0], edge[1])['capacity'][w])

    def output_to_logfile(self, prediction: str, n: int):
        logger.info('It is the ' + str(n) + " simulation times, and the mode is: " + prediction)
        logger.info('the penalty is: ' + str(self.penalty))
        # logger.info(self.transfer_traffic)
        logger.info('the transfer traffic is: ' + str(np.sum(self.transfer_traffic)))
        # logger.info(self.failure)
        logger.info('++++++++++++++++++++++++++++++++')


def main(network: PhysicalNetwork.NetworkEnvironment, n: int, prediction: bool, mode: int,
         reservation: float, slices: list):
    network.reset()
    heuristic = PredictionNSM(network, C.TOTAL_TIME, slices)
    heuristic.resetSlices()
    heuristic.initialize(reservation)
    for i in range(1, C.TOTAL_TIME):
        if mode == 1:
            heuristic.Fit(i)
        elif mode == 2:
            heuristic.OverProvision(i, reservation)
        else:
            heuristic.adjustPrediction(i, prediction)
        # heuristic.showRequest()
    heuristic.output_to_logfile(str(prediction), n)
    heuristic.network.usage_edge()
    print(np.sum(heuristic.failure))
    return heuristic.penalty, np.sum(heuristic.transfer_traffic), heuristic.failure


if __name__ == "__main__":

    network = MetroNetwork.NetworkEnvironment("LargeTopology_link", "/home/mario/PycharmProjects/PredictionNSM/Resource")