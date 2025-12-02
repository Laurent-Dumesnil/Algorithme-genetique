#   ____                      __  __       _        _   _             ____  _             _                   
#  / ___| ___ _ __   ___  ___|  \/  |_   _| |_ __ _| |_(_) ___  _ __ / ___|| |_ _ __ __ _| |_ ___  __ _ _   _ 
# | |  _ / _ \ '_ \ / _ \/ __| |\/| | | | | __/ _` | __| |/ _ \| '_ \\___ \| __| '__/ _` | __/ _ \/ _` | | | |
# | |_| |  __/ | | |  __/\__ \ |  | | |_| | || (_| | |_| | (_) | | | |___) | |_| | | (_| | ||  __/ (_| | |_| |
#  \____|\___|_| |_|\___||___/_|  |_|\__,_|\__\__,_|\__|_|\___/|_| |_|____/ \__|_|  \__,_|\__\___|\__, |\__, |
#                                                                                                 |___/ |___/ 



import numpy as np
from numpy.typing import NDArray


from gacvm import MutationStrategy, Domains


class GenesMutationStrategy(MutationStrategy):
    """Stratégie de mutation qui mute tous les gènes d'un individu à la fois.
    
    La mutation est effectuée sur chaque gène d'un individu avec la probabilité donnée.
    """
    
    def __init__(self) -> None:
        super().__init__('Mutate All Genes')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                offspring[:] = domains.random_values()
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
