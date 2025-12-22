#   ____                      __  __       _        _   _             ____  _             _                   
#  / ___| ___ _ __   ___  ___|  \/  |_   _| |_ __ _| |_(_) ___  _ __ / ___|| |_ _ __ __ _| |_ ___  __ _ _   _ 
# | |  _ / _ \ '_ \ / _ \/ __| |\/| | | | | __/ _` | __| |/ _ \| '_ \\___ \| __| '__/ _` | __/ _ \/ _` | | | |
# | |_| |  __/ | | |  __/\__ \ |  | | |_| | || (_| | |_| | (_) | | | |___) | |_| | | (_| | ||  __/ (_| | |_| |
#  \____|\___|_| |_|\___||___/_|  |_|\__,_|\__\__,_|\__|_|\___/|_| |_|____/ \__|_|  \__,_|\__\___|\__, |\__, |
#                                                                                                 |___/ |___/ 

# -----------------------------------------
# Stratégie de mutation Adaptative
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
from ga_strategy_genes_mutation import GenesMutationStrategy
from ga_custom_strategy import GeneralMutationStrategy, ExploitativeMutationStrategy


class AdaptiveMutationStrategies(MutationStrategy):
    def __init__(self):
        super().__init__('Adaptive Mutation Strategies')
        self.__mutation_strategy_list = [GeneralMutationStrategy, ExploitativeMutationStrategy]
        self.__prob_list = np.array([0.3, 0.7])

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()
        selected_strategy = rng.choice(self.__mutation_strategy_list, p=self.__prob_list)
        selected_strategy.mutate(self, offsprings, mutation_rate, domains)
             
        