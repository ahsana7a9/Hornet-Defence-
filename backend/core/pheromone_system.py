class PheromoneSystem:
    def __init__(self):
        self.threats = {}

    def mark(self, target):
        if target not in self.threats:
            self.threats[target] = 1
        else:
            self.threats[target] += 1

        print(f"[Pheromone] Threat tagged: {target}")
