#   ____                      __  __       _        _   _             ____  _             _                   
#  / ___| ___ _ __   ___  ___|  \/  |_   _| |_ __ _| |_(_) ___  _ __ / ___|| |_ _ __ __ _| |_ ___  __ _ _   _ 
# | |  _ / _ \ '_ \ / _ \/ __| |\/| | | | | __/ _` | __| |/ _ \| '_ \\___ \| __| '__/ _` | __/ _ \/ _` | | | |
# | |_| |  __/ | | |  __/\__ \ |  | | |_| | || (_| | |_| | (_) | | | |___) | |_| | | (_| | ||  __/ (_| | |_| |
#  \____|\___|_| |_|\___||___/_|  |_|\__,_|\__\__,_|\__|_|\___/|_| |_|____/ \__|_|  \__,_|\__\___|\__, |\__, |
#                                                                                                 |___/ |___/ 



import numpy as np
from numpy.typing import NDArray


from gacvm import MutationStrategy, Domains


class OneGeneMutationStrategy(MutationStrategy):
    def __init__(self) -> None:
        super().__init__('Mutate One Gene')

    #si un gène est proche de la borne max ou min, muter vers l’autre côté pour éviter stagnation

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()
        for child in offsprings:

            if rng.random() <= mutation_rate:
                n_dim = domains.ranges.shape[0]
                gene_cible = rng.integers(0, n_dim)
                val_max = domains.ranges[gene_cible, 1]
                val_min = domains.ranges[gene_cible, 0]

                milieu = (np.abs(val_max) - np.abs(val_min))/2

                if child[gene_cible] < milieu or child[gene_cible] == 0:
                    child[gene_cible] = child[gene_cible] *2
                else:
                    child[gene_cible] = child[gene_cible] /2