#   ____                      __  __       _        _   _             ____  _             _                   
#  / ___| ___ _ __   ___  ___|  \/  |_   _| |_ __ _| |_(_) ___  _ __ / ___|| |_ _ __ __ _| |_ ___  __ _ _   _ 
# | |  _ / _ \ '_ \ / _ \/ __| |\/| | | | | __/ _` | __| |/ _ \| '_ \\___ \| __| '__/ _` | __/ _ \/ _` | | | |
# | |_| |  __/ | | |  __/\__ \ |  | | |_| | || (_| | |_| | (_) | | | |___) | |_| | | (_| | ||  __/ (_| | |_| |
#  \____|\___|_| |_|\___||___/_|  |_|\__,_|\__\__,_|\__|_|\___/|_| |_|____/ \__|_|  \__,_|\__\___|\__, |\__, |
#                                                                                                 |___/ |___/ 

# -----------------------------------------
# Stratégie de mutation exploitative
# -----------------------------------------
# Auteurs :
# Mario Laframboise
# Laurent Dumesnil
# Julien Lamontagne
# Guillaume Foisy
# Eduardo Eugenio Gomez Torres
# -----------------------------------------
# date : 22 décembre 2025
# -----------------------------------------


import numpy as np
from numpy.typing import NDArray


from gacvm import MutationStrategy, Domains


class AdaptiveMutationStrategy(MutationStrategy):
    """ Stratégie de mutation exploitative"""
    def __init__(self) -> None:
        super().__init__('Adaptive Mutation')

    #Décrémentation progressive du taux de mutation.

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()
        stds = np.std(offsprings, axis=0)
        ranges = domains.ranges[:, 1] - domains.ranges[:, 0]
        diversity = np.mean(stds / ranges)
        
        mutation_multiple = 0.3

        n_dim = domains.ranges.shape[0]

        for child in offsprings:
            if rng.random() <= mutation_rate:
                if rng.random() <= mutation_multiple:
                    nb_mutation = rng.integers(2, n_dim +1)
                    genes_cible = rng.choice(n_dim, size = nb_mutation, replace = False)
                else:
                    genes_cible = [rng.integers(0, n_dim)]

                for gene in genes_cible:
                    val_min, val_max = domains.ranges[gene]
                    # if rng.random() < 0.1:
                    #     nb_reset = rng.integers(2, n_dim + 1)
                    #     reset_genes = rng.choice(n_dim, size=nb_reset, replace=False)
                    #     for gene in reset_genes:
                    #         val_min, val_max = domains.ranges[gene]
                    #         child[gene] = rng.uniform(val_min, val_max)
                    #         continue
                    # else:
                    k = np.exp(-diversity * 5) 
                    amplitude = 0.1 * k * (val_max - val_min)

                    child[gene] += rng.normal(0, amplitude)
                    child[gene] = np.clip(child[gene], val_min, val_max)


        # mask1 = rng.random(offsprings.shape) <= mutation_rate
        # mask2 = (mask1 == True) & (rng.random(offsprings.shape) <= mutation_multiple)
        # mask3 = (mask1 == True) & (mask2 == False)

        # nb_mutation = rng.integers(2, n_dim + 1, offsprings.shape[0])
        # genes_cible = rng.choice(n_dim, size = nb_mutation, replace = False)

        pass


