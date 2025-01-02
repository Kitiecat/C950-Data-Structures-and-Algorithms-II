
import queue

class Vertex:
    def __init__(self, name, adjVertexes):
        self.name = name
        self.value = None
        self.distance = None
        self.predecessor = None
        self.adjVertexes = adjVertexes
        pass

A = Vertex("A", [["B", 3],["C", 7]])
B = Vertex("B", [["C", 5],["D", 1]])
C = Vertex("C", [["D", 9]])
D = Vertex("D", [["C", 2]])

graph = {
    "A" : A,
    "B" : B,
    "C" : C,
    "D" : D}

def dijkstra_shortest_path(startV):
    unvisitedQueue = queue.Queue()
    for key, vertex in graph.items():
        vertex.distance = float('inf')
        vertex.predecessor = 0
        unvisitedQueue.put(vertex)

    startV.distance = 0

    while ( not unvisitedQueue.empty()):
        currentV = unvisitedQueue.get()


        for adjV in currentV.adjVertexes:
            edgeWeight = adjV[1]
            alternativePathDistance = currentV.distance + edgeWeight
            if (alternativePathDistance < graph.get(adjV[0]).distance):
                graph.get(adjV[0]).distance = alternativePathDistance
                graph.get(adjV[0]).predV = currentV

def main():
    dijkstra_shortest_path(graph.get("A"))

if __name__ == "__main__":
    main()