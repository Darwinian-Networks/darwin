class BayesianNetwork:

    def __init__(self):
        self.potentials = []
        self.dag = None

    def add_potential(self, potential):
        self.potentials.append(potential)

    def add_dag(self, dag):
        self.dag = dag
