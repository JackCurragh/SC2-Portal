class Transcript_graph(object):
    def __init__(self, transcript_length, graph=None):
        """
        Takes a nested dictionary as input with nodes as keys.
        Each node subdictionary has values in and out which are used to get the direction of edges.
        """
        if graph == None:
            graph = {1: Node(1, "nc", 1, (0, transcript_length), 1)}
            # graph = {}
        self.node_count = len(graph.keys())
        self.graph = graph

    def vertices(self):
        """
        return a list of the vertices/nodes from the graph
        """
        return list(self.graph.keys())

    def get_new_key(self):
        """
        check the graph to find the lowest available key
        """
        keys = self.vertices()
        if len(keys) > 0:
            return max(keys) + 1
        else:
            return 1

    def get_overlaps_with_node(self, new_node):
        """
        Checks the overlaps between an inputed node object and the existing nodes in the graph

        Returns list of tuples with form (nodes, <overlap point>)
        """
        overlaps = []
        new_node_coords = (new_node.node_start, new_node.node_stop)
        for node in self.graph:
            node_coords = (self.graph[node].node_start, self.graph[node].node_stop)

            if new_node_coords[0] in range(node_coords[0], node_coords[1] - 1):
                overlaps.append((node, "start", self.graph[node].height))
            if new_node_coords[1] in range(node_coords[0] + 1, node_coords[1]):
                overlaps.append((node, "stop", self.graph[node].height))

        return overlaps

    def resolve_overlaps(self, overlaps, node, inherited=None):
        """
        Reformats the existing nodes in the graph to cater for the inclusion of node to be included

        if node solely overlaps with one 'nc' node then the nc node is split

        else adjust heights to avoid conflicts



        This function contains a bug.
        Nc node is removed meaning the length of overlaps when add vertex is called is 0. Meaning the node is added with type same as new node

        perhaps the add vertex funciton used in this should be different to the one that calls this funciton
        """

        # if this if is satisfied then the overlap is solely with nc node
        if len(overlaps) == 2 and (overlaps[0][0] == overlaps[-1][0]):
            nc_node = self.get_vertex(overlaps[0][0])
            self.drop_vertex(nc_node)
            self.add_vertex_no_overlaps(
                nc_node.node_type,
                nc_node.frame,
                (nc_node.node_start, node.node_start),
                nc_node.height,
            )  # nc start -> coding_start   A
            self.add_vertex_no_overlaps(
                nc_node.node_type,
                nc_node.frame,
                (node.node_stop, nc_node.node_stop),
                nc_node.height,
            )  # coding stop -> non coding stop  B

            self.add_vertex_no_overlaps(
                node.node_type,
                node.frame,
                (node.node_start, node.node_stop),
                nc_node.height,
            )  # C

            # edges to add A - C / C - B
            updated_keys = {
                entry: self.graph[entry].node_start for entry in self.graph.keys()
            }
            for entry1 in updated_keys:
                for entry2 in updated_keys:
                    # A - C
                    if (
                        updated_keys[entry1] == nc_node.node_start
                        and updated_keys[entry2] == node.node_start
                    ):
                        self.add_edge(entry1, entry2)
                    elif (
                        updated_keys[entry2] == node.node_start
                        and updated_keys[entry1] == node.node_stop
                    ):
                        self.add_edge(entry1, entry2)

        elif len(overlaps) == 0:  # no overlaps so nothing to worry about
            pass
        else:  # coding overlap means add node with different height. Use one based increase in height so scaling can be done in plotting
            heights = [i[2] for i in overlaps]
            self.add_vertex_no_overlaps(
                node.node_type,
                node.frame,
                (node.node_start, node.node_stop),
                max(heights) + 1,
            )

    def add_vertex_no_overlaps(self, node_type, frame, coordinates, height):
        self.node_count += 1
        new_key = self.get_new_key()
        new_vertex = Node(new_key, node_type, frame, coordinates, height)
        self.graph[new_key] = new_vertex

    def add_vertex(self, node_type, frame, coordinates):
        self.node_count += 1
        new_key = self.get_new_key()
        new_vertex = Node(new_key, node_type, frame, coordinates, 1)
        overlaps = self.get_overlaps_with_node(new_vertex)
        self.resolve_overlaps(overlaps, new_vertex)

        # self.graph[new_key] = new_vertex

        return new_vertex

    def get_vertex(self, key):
        if key in self.graph:
            return self.graph[key]
        else:
            return None

    def add_edge(self, node1, node2, weight=0):
        if node1 not in self.graph:
            self.add_vertex(node1)
        if node2 not in self.graph:
            self.add_vertex(node2)

        self.graph[node1].add_neighbour(node2, weight)
        self.graph[node2].add_neighbour(node1, weight)

    def drop_vertex(self, node):
        """
        first remove the edges then remove the node itself
        """
        node_neighbours = node.connected
        for neighbour in node_neighbours:
            self.graph[neighbour].connected.pop(node.key)

        self.graph.pop(node.key)
        self.node_count -= 1

    def statistics(self):
        stats = {}
        nodes = list(self.graph.keys())
        calc_dict = {
            "edges": [],
            "frames": [],
            "types": [],
            "heights": [],
            "frames_freq": {},
            "types_freq": {},
            "heights_freq": {},
        }

        for i in nodes:
            for j in self.graph[i].connected:
                if (j, i) not in calc_dict["edges"]:
                    calc_dict["edges"].append((i, j))

            calc_dict["frames"].append(self.graph[i].frame)
            calc_dict["types"].append(self.graph[i].node_type)
            calc_dict["heights"].append(self.graph[i].height)

        for item in calc_dict["frames"]:
            if item in calc_dict["frames_freq"]:
                calc_dict["frames_freq"][item] += 1
            else:
                calc_dict["frames_freq"][item] = 1

        for item in calc_dict["types"]:
            if item in calc_dict["types_freq"]:
                calc_dict["types_freq"][item] += 1
            else:
                calc_dict["types_freq"][item] = 1

        for item in calc_dict["heights"]:
            if item in calc_dict["heights_freq"]:
                calc_dict["heights_freq"][item] += 1
            else:
                calc_dict["heights_freq"][item] = 1

        for item in calc_dict["types_freq"]:
            key = "Number_of_" + item
            stats[key] = calc_dict["types_freq"][item]

        for item in calc_dict["frames_freq"]:
            key = "Number_of_nodes_in_frame_" + str(item)
            stats[key] = calc_dict["frames_freq"][item]

        for item in calc_dict["heights_freq"]:
            key = "Number_of_nodes_with_height_" + str(item)
            stats[key] = calc_dict["heights_freq"][item]

        stats["Node_keys"] = nodes
        stats["Number_of_nodes"] = self.node_count
        stats["Edges_keys"] = calc_dict["edges"]
        stats["Number_of_edges"] = len(calc_dict["edges"])
        stats["Number_of_node_types"] = len(calc_dict["types_freq"])

        return stats

    def describe(self):
        """
        print in the terminal a description of the graph
        """

        stats = self.statistics()
        for entry in stats:
            print(str(entry) + "\t" + str(stats[entry]))

    def node_to_svg(self, node):
        h = node.height
        if node.node_type == "nc":
            M = (str(node.node_start), str((node.height + 2 + h * 5) / 10))
            L1 = (str(node.node_start), str((node.height + 4 + h * 5) / 10))
            L2 = (str(node.node_stop), str((node.height + 4 + h * 5) / 10))
            L3 = (str(node.node_stop), str((node.height + 2 + h * 5) / 10))
            colour = "black"
        else:
            M = (str(node.node_start), str((node.height + 1 + h * 5) / 10))
            L1 = (str(node.node_start), str((node.height + 5 + h * 5) / 10))
            L2 = (str(node.node_stop), str((node.height + 5 + h * 5) / 10))
            L3 = (str(node.node_stop), str((node.height + 1 + h * 5) / 10))

            if node.frame == 0:
                colour = "red"
            elif node.frame == 1:
                colour = "blue"
            elif node.frame == 2:
                colour = "green"
        string = """
            {
            type: 'path', 
            path: ' M %s,%s L %s,%s L %s,%s L %s,%s L %s,%s Z', 
            fillcolor: '%s',
            line: {color: 'black'}
            },""" % (
            M[0],
            M[1],
            L1[0],
            L1[1],
            L2[0],
            L2[1],
            L3[0],
            L3[1],
            M[0],
            M[1],
            colour,
        )
        return string

    def graph_to_js_plotly(self):

        shape_string = ""
        nodes = list(self.graph.keys())
        last_node = nodes[-1]
        for node in self.graph:
            shape_string += self.node_to_svg(self.graph[node])
            if node != last_node:
                shape_string = shape_string + " \n"

        file_head = """
{% extends 'base.html' %}

{% block content %}
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<div id="plot_div" style="width: 100%; height: 100%"></div>

<script type="text/javascript">


var trace1 = {
  x: [1],
  y: [9],
  text: ['filled polygon'],
  mode: 'text'
};

var layout = {
  title: 'Transcript Graph of SARS-CoV2 gRNA',
  xaxis: {
    range: [0, 30000],
    visible: false
  },
  yaxis: {
    range: [-5, 3],
    visible: false

  },

  width: 750,
  height: 500,
  shapes: [

        """
        file_tail = """ 
  ]


};
var data = [trace1];

    Plotly.newPlot("plot_div", data, layout);

</script>



{% endblock %}

        """
        with open("templates/transcriptGraph.html", "w") as f:
            f.write(file_head)
            f.write(shape_string)
            f.write(file_tail)

        return shape_string


class Node(object):
    def __init__(self, key, node_type, frame, coordinates, height):
        self.key = key
        self.node_type = node_type
        self.connected = {}
        self.frame = frame
        self.node_start = coordinates[0]
        self.node_stop = coordinates[1]
        self.height = height

    def add_neighbour(self, neighbour, weight=0):
        self.connected[neighbour] = weight

    def get_connections(self):
        return self.connected.keys()

    def node_key(self):
        return self.key

    def node_type(self):
        return self.node_type

    def node_frame(self):
        return self.frame

    def get_neighbour_weight(self, neighbour):
        return self.connected[neighbour]


# if __name__ == "__main__":

#     g = { "a" : {"out":[], "in":[]},
#           "b" : {"out":[], "in":[]},
#           "c" : {"out":[], "in":[]},
#           "d" : {"out":[], "in":[]},
#           "e" : {"out":[], "in":[]},
#           "f" : {"out":[], "in":[]}
#         }


#     graph = Transcript_graph(g)

#     Transcript_graph.edges(graph)
#     Transcript_graph.add_edge(graph, 'a', 'b')
#     Transcript_graph.add_edge(graph, 'b', 'g')

#     print(Transcript_graph.edges(graph))
#     print(Transcript_graph.vertices(graph))
#     print(Transcript_graph.graph)
