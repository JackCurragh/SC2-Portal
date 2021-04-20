
class Transcript_graph(object):

    def __init__(self, graph=None):
        if graph == None:
            graph = {}
        self.graph = graph 
    
    def vertices(self):
        return list(self.graph.keys())
    
    def edges(self):
        return self.get_edges()

    def get_edges(self):
        edges =[]
        for vertex in self.vertices():
            for edge in self.graph[vertex]['out']:
                if (vertex, edge) not in edges:
                    edges.append((vertex, edge))

            for edge in self.graph[vertex]['in']:
                if (edge, vertex) not in edges:
                    edges.append((edge, vertex))
        return edges 

    def add_vertex(self, vertex, edges=[]):
        if vertex not in self.graph:
            if edges != []:
                self.graph[vertex] = {"out":[edge[1] for edge in edges], "in":[edge[0] for edge in edges]}

            else:
                self.graph[vertex] = {"out":[], "in":[]}

    def add_edge(self, outward, inward):
        if (outward in self.graph) and (inward in self.graph):
            self.graph[outward]["out"].append(inward)
            self.graph[inward]["in"].append(outward)
        else:
            self.add_vertex(outward)
            self.add_vertex(inward)
            self.graph[outward]["out"].append(inward)
            self.graph[inward]["in"].append(outward)




if __name__ == "__main__":

    g = { "a" : {"out":[], "in":[]},
          "b" : {"out":[], "in":[]},
          "c" : {"out":[], "in":[]},
          "d" : {"out":[], "in":[]},
          "e" : {"out":[], "in":[]},
          "f" : {"out":[], "in":[]}
        }


    graph = Transcript_graph(g)

    Transcript_graph.edges(graph)
    Transcript_graph.add_edge(graph, 'a', 'b')
    Transcript_graph.add_edge(graph, 'b', 'g')

    print(Transcript_graph.edges(graph))
    print(Transcript_graph.vertices(graph))
