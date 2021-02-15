import tkinter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import networkx as nx
import PhysicalNetwork



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pNetwork = PhysicalNetwork.NetworkEnvironment("SmallTopology_link",
                                              "/home/hao/PycharmProjects/DLNSD/Resource")
    pNetwork.reset()
    #pNetwork.usage_edge()
    plt.subplot(111)
    nx.draw(pNetwork, with_labels=True, font_weight='bold')
    # plt.show()

    path=('1','2','5','4')
    pNetwork.set_wave_capacity_edge(('2','5'),6,0,1,True)
    pNetwork.set_wave_capacity_edge(('1','2'),6,1,1,True)
    pNetwork.set_wave_capacity_edge(('5','4'),6,2,1,True)
    wave = pNetwork.first_fit_wavelength(path,5)
    print(wave)
    print(pNetwork.has_edge('3','6'))




