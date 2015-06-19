import networkx as nx


def d_separation(X, Y, Z, DAG):

    # Phase I: ancestors of Y
    AnY = set()
    for y in Y:
        AnY = AnY.union(nx.ancestors(DAG, y))
    A = AnY.union(Y)

    # Phase II: traverse active paths starting from X
    L = []
    V = []
    R = []

    for v in X:
        L.append(("up", v))

    while len(L) > 0:

        (d, v) = L.pop()

        if (d, v) not in V:
            V.append((d, v))
            if v not in Y:
                R.append(v)

            if (d == "up") and (v not in Y):
                for vi in DAG.predecessors(v):
                    L.append(("up", vi))
                for vi in DAG.successors(v):
                    L.append(("down", vi))
            elif d == "down":
                if v not in Y:
                    for vi in DAG.successors(v):
                        L.append(("down", vi))
                if v in A:
                    for vi in DAG.predecessors(v):
                        L.append(("up", vi))

    # Test Independence
    independence = True
    if len(set(Z).intersection(set(R))) > 0:
        independence = False

    return independence
