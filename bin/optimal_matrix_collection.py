# A Python program for Prim's Minimum Spanning Tree (MST) algorithm.
# The program is for adjacency matrix representation of the graph

import sys  # Library for INT_MAX
import numpy as np
from scipy.spatial import distance
import pandas as pd


class Graph():

    def __init__(self, xCoords, yCoords, substation_x, substation_y):
        self.V = len(xCoords)+1
        self.seg2sub = np.zeros(self.V)  # number of segments from vertex to substation
        self.weight = 0  # weight that seg2sub adds to prim algorithm (to keep cables small). USER INPUT.
        # print('collection weight factor = '+str(self.weight))
        self.graph = [[0 for column in range(self.V)]
                      for row in range(self.V)]
        self.adj = [[0 for column in range(self.V)]
                      for row in range(self.V)]
        self.xCoords = list(xCoords)
        self.yCoords = list(yCoords)
        # zeroth node is substation, which is in the center of the farm
        # if self.V > 2:
        #     self.xCoords.insert(0, np.mean(self.xCoords))
        #     self.yCoords.insert(0, np.mean(self.yCoords))
        #     self.substation_xy = pd.DataFrame([self.xCoords[0], self.yCoords[0]])
        # else:
        #     substation_x = self.xCoords[0] + 50
        #     self.xCoords.insert(0, substation_x)
        #     substation_y = self.yCoords[0] + 50
        #     self.yCoords.insert(0, substation_y)
        #     self.substation_xy = pd.DataFrame([self.xCoords[0], self.yCoords[0]])
        self.xCoords.insert(0, substation_x)
        self.yCoords.insert(0, substation_y)
        self.substation_xy = pd.DataFrame([substation_x, substation_y])
        self.create_graph()


    def create_graph(self):
        bpkt = 0;
        # create graph with distances from each node to each other node.
        for i in range(0, self.V):
            pti = [self.xCoords[i], self.yCoords[i]]
            for j in range(0, self.V):
                ptj = [self.xCoords[j], self.yCoords[j]]
                self.graph[i][j] = distance.euclidean(pti, ptj)


    def printMST(self, parent):
        # A utility function to print the constructed MST stored in parent[]
        # print("Edge \tWeight")
        for i in range(1, self.V):
            # print(parent[i], "-", i, "\t", self.graph[i][parent[i]])
            self.adj[parent[i]][i] = 1
            self.adj[i][parent[i]] = 1
        self.adjdf = pd.DataFrame(self.adj)

    # minimum distance value, from the set of vertices
    # not yet included in shortest path tree
    def minKey(self, key, mstSet):

        # Initilaize min value
        min = sys.maxsize

        for v in range(self.V):
            if key[v] < min and mstSet[v] == False:
                min = key[v]
                min_index = v

        return min_index

        # Function to construct and print MST for a graph

    # represented using adjacency matrix representation
    def primMST(self):

        # Key values used to pick minimum weight edge in cut
        key = [sys.maxsize] * self.V
        parent = [None] * self.V  # Array to store constructed MST
        # Make key 0 so that this vertex is picked as first vertex
        key[0] = 0
        mstSet = [False] * self.V

        parent[0] = -1  # First node is always the root of

        for cout in range(self.V):

            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to src in first iteration
            u = self.minKey(key, mstSet)

            # Put the minimum distance vertex in
            # the shortest path tree
            mstSet[u] = True
            # increment # segments to substation: each vertex is one segment farther to the substation than its parent
            self.seg2sub[u] = self.seg2sub[parent[u]]+1 #TODO put back in

            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shortest path tree
            for v in range(self.V):
                # graph[u][v] is non zero only for adjacent vertices of m
                # mstSet[v] is false for vertices not yet included in MST
                # Update the key only if graph[u][v] is smaller than key[v]
                self.graph[u][v] *= (1+self.seg2sub[u]*self.weight) # update weight matrix with correct weight #TODO uncomment
                if self.graph[u][v] > 0 and mstSet[v] == False and key[v] > self.graph[u][v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u

        self.printMST(parent)
