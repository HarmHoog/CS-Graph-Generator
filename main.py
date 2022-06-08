import networkx as nx

# Set this to true if discriminative tuples should be generated from combinations of generative
generateDiscriminative = True

# The folder where the tuples are stored.
dataFolder = "datasmall"


# Data class for generative tuples
class GenTuple:

    def __init__(self, sign, concept, relation, inp):
        self.sign = sign
        self.concept = concept
        self.relation = relation
        self.inp = inp


# Data class for discriminative tuples
class DiscrTuple:

    def __init__(self, sign, concept_a, concept_b, relation, inp):
        self.sign = sign
        self.conceptA = concept_a
        self.conceptB = concept_b
        self.relation = relation
        self.inp = inp

    def __hash__(self):
        return hash((self.sign, self.relation, self.inp))

    def __eq__(self, other):
        if self.sign != other.sign or self.relation != other.relation or self.inp != other.inp:
            return False

        return (self.conceptA == other.conceptA and self.conceptB == other.conceptB) or \
               (self.conceptA == other.conceptB and self.conceptB == other.conceptA)


def generate_output(graphx, name):
    g = nx.nx_agraph.to_agraph(graphx)
    g.graph_attr["overlap"] = "scale"
    g.node_attr["style"] = "filled"
    g.node_attr["fillcolor"] = "white"

    g.layout("sfdp")
    g.draw("output/" + name + ".png")
    g.draw("output/" + name + ".ps")


def add_generative(graph):
    for tup in posGenTuples:
        graph.add_edge(tup.concept, tup.inp, color="green", xlabel=tup.sign + tup.relation)

    for tup in negGenTuples:
        graph.add_edge(tup.concept, tup.inp, color="red", xlabel=tup.sign + tup.relation)


def add_discriminative(graph):
    for tup in posDiscrTuples:
        graph.add_edge(tup.conceptA, tup.conceptB, color="blue", xlabel=tup.sign + tup.relation + " " + tup.inp)
    for tup in negDiscrTuples:
        graph.add_edge(tup.conceptA, tup.conceptB, color="orange", xlabel=tup.sign + tup.relation + " " + tup.inp, dir="none")


# Load both the positive and negative generative tuples
print("Loading generative positive tuples")
posGenTuples = []
with open(dataFolder + '/positive_triples.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        row = line.strip('\n').split("|")
        posGenTuples.append(GenTuple("+", row[0], row[1], row[2]))
negGenTuples = []
print("Loading generative negative tuples")
with open(dataFolder + '/negative_triples.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        row = line.strip('\n').split("|")
        negGenTuples.append(GenTuple("-", row[0], row[1], row[2]))

posDiscrTuples = []
negDiscrTuples = set()
if not generateDiscriminative:
    # Load the positive discriminative tuples
    print("Loading discriminative positive tuples")
    with open('datasmall/positive_discriminative_knowledge.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            row = line.strip('\n').split("|")
            posDiscrTuples.append(DiscrTuple("+", row[0], row[1], row[2], row[3]))

    # Load the negative discriminative tuples. Since these are not directed and stored both ways
    # we need to filter the duplicates
    print("Loading discriminative negative tuples")
    with open('datasmall/negative_discriminative_knowledge.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            row = line.strip('\n').split("|")
            negDiscrTuples.add(DiscrTuple("-", row[0], row[1], row[2], row[3]))
else:
    print("Generating discriminative positive tuples")
    for p in posGenTuples:
        for n in negGenTuples:
            if p.relation == n.relation and p.inp == n.inp:
                posDiscrTuples.append(DiscrTuple("+", p.concept, n.concept, p.relation, p.inp))
    print("Generating discriminative negative tuples")
    for p in posGenTuples:
        for p2 in posGenTuples:
            if p.concept != p2.concept and p.relation == p2.relation and p.inp == p2.inp:
                negDiscrTuples.add(DiscrTuple("-", p.concept, p2.concept, p.relation, p.inp))
    for n in negGenTuples:
        for n2 in negGenTuples:
            if n.concept != n2.concept and n.relation == n2.relation and n.inp == n2.inp:
                negDiscrTuples.add(DiscrTuple("-", n.concept, n2.concept, n.relation, n.inp))

# Generate a generative graph with both negative and positive tuples
print("Generating generative graph")
GG = nx.MultiDiGraph(outputorder="edgesfirst")
add_generative(GG)

generate_output(GG, "generative")
print("Generative graph saved")

# Generate a discriminative graph with both negative and positive tuples
print("Generating discriminative graph")
DG = nx.MultiDiGraph(outputorder="edgesfirst")
add_discriminative(DG)

generate_output(DG, "discriminative")
print("Discriminative graph saved")

# Generate a combined graph with both negative, positive, discriminative and generative tuples
print("Generating combined (generative and discriminative) graph")
CombG = nx.MultiDiGraph(outputorder="edgesfirst")

add_generative(CombG)
add_discriminative(CombG)

generate_output(CombG, "combined")
print("Combined graph saved")

print("Generating hyper graph")
HyperG = nx.MultiDiGraph(outputorder="edgesfirst")
hyperedgesPos = dict()
hyperedgesNeg = dict()

for t in posGenTuples:
    if (t.relation, t.inp) not in hyperedgesPos:
        hyperedgesPos[(t.relation, t.inp)] = set()
    hyperedgesPos[(t.relation, t.inp)].add(t.concept)
for t in negGenTuples:
    if (t.relation, t.inp) not in hyperedgesNeg:
        hyperedgesNeg[(t.relation, t.inp)] = set()
    hyperedgesNeg[(t.relation, t.inp)].add(t.concept)

for k, v in hyperedgesPos.items():
    node = "+" + k[0] + " " + k[1]
    HyperG.add_node(node, fillcolor="lightgreen", shape="pentagon", label=k[0])
    HyperG.add_edge(node, k[1])
    for t in v:
        HyperG.add_edge(t, node)

for k, v in hyperedgesNeg.items():
    node = "-" + k[0] + " " + k[1]
    HyperG.add_node(node, fillcolor="lightsalmon", shape="pentagon", label=k[0])
    HyperG.add_edge(node, k[1])
    for t in v:
        HyperG.add_edge(t, node)

generate_output(HyperG, "hypergraph")
print("Hyper graph saved")
