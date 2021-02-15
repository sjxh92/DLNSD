import pandas as pd
from PhysicalNetwork import NetworkEnvironment as network
import PhysicalNetwork
import networkx as nx
import itertools

test_dict = {'id':[1,2,3,4,5,6],
             'name':['Alice','Bob','Cindy','Eric','Helen','Grace '],
             'math':[90,89,99,78,97,93],
             'english':[89,94,80,94,94,90],
             'path':[(1,3,4),(1,2),(1,4),(1,5),(1,7),(1,6)]}
test_dict_df = pd.DataFrame(test_dict)
print(test_dict_df)

print(type(test_dict_df.loc[2,'path']))

print(test_dict_df.loc[test_dict_df['path']==(1,3,4)])

def a():
    if (not test_dict_df.loc[test_dict_df['path']==(2,5)].empty):
        print('exist')
        return True
    else:
        print('noexist')
        return False
print(a())

def extract_path(nodes:tuple):
    assert len(nodes) >= 2
    rtn = []
    start_node = nodes[0]
    for i in range(1, len(nodes)):
        end_node = nodes[i]
        rtn.append((start_node, end_node))
        start_node = end_node
    return rtn

print(extract_path((1,3,4,5,6,7)))
print(test_dict_df.loc[1,'english'])
test_dict_df.loc[1,'english']+=6
print(test_dict_df.loc[1,'english'])

path = (1,2,3,4,5)
pairs = PhysicalNetwork.extract_path_pro(path)
print(pairs)

graph = nx.DiGraph()
graph.add_edge(1,3)
graph.add_edge(3,4)
graph.add_edge(4,6)
graph.add_edge(5,6)
# nx.shortest_simple_paths(graph, 1, 6)
# nx.shortest_path(graph, 1, 6)
path = nx.single_source_dijkstra_path(graph,source=1)
print(path.get(6))
a = (1,2,3,4)
print(a[-1])

for i in range(6,1,-1):
    print(i)
print('========================')
path = [1,2,3,4,5,6,7]
paths = {}

for i in itertools.combinations((1,2,3,4,5), 2):
    print(i)
    #print(''.join(i),end=" ")

a = [1,2,3,4,5,0,6,7,8]
print(a.index(max(a)))
