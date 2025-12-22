import numpy as np
from numpy.typing import NDArray


from gacvm import MutationStrategy, Domains
from gacvm import SelectionStrategy

def local_exploration(index_local, editable_dim, offsprings, domains, rng):
        ranges = domains.ranges[:editable_dim]
        mins = ranges[:, 0]
        maxs = ranges[:, 1]
        matrice_etendu = maxs - mins

        #On y va des step de 3% de notre etendu de domaine
        steps = 0.03 * matrice_etendu

        #semble donner un meilleur resultat avec normal que uniform mais à vérifier
        value = rng.normal(0.0, steps, size=(index_local.size, editable_dim))

        offsprings[index_local, :editable_dim] += value

        # Clipping vectorisé
        offsprings[index_local, :editable_dim] = np.clip(offsprings[index_local, :editable_dim], mins, maxs)

def global_exploration(offsprings, domains, index_global, editable_dim, rng):
    ranges = domains.ranges[:editable_dim]
    mins = ranges[:, 0]
    maxs = ranges[:, 1]

    offsprings[index_global, :editable_dim] = rng.integers(mins, maxs, size=(index_global.size, editable_dim))
                


class GeometryMutationStrategy(MutationStrategy):
    def __init__(self) -> None:
        super().__init__('Geometry mutation strategy')

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()

        n_children, n_dim = offsprings.shape
        editable_dim = n_dim - 1  # on exclut la dernière dimension de scaling

        # Masque pour savoir quels enfants mutent
        mask_children = rng.random(n_children) <= mutation_rate
        index_mutate_children = np.where(mask_children)[0]

        #Si on a pas d'enfant qui mutent
        if index_mutate_children.size == 0:
            return

        # Masque pour savoir si on fait une exploration globale (True) ou locale (False)
        #70% va etre de l'exploration globale et 30% de l'exploration locale
        mask_global = rng.random(index_mutate_children.size) <= 0.7

        # Exploration Global
        index_global = index_mutate_children[mask_global]
        if index_global.size > 0:
           global_exploration(offsprings, domains, index_global, editable_dim, rng)

        # Exploration local
        index_local = index_mutate_children[mask_global == False]
        if index_local.size > 0:
            local_exploration(index_local, editable_dim, offsprings, domains, rng)
            
                
        # tentative d'expansion
        scale_index = 3
        scale_min, scale_max = domains.ranges[scale_index]
        scale_step = 0.01 * (scale_max - scale_min)

        # Masque pour savoir ceux qui vont essayer un scaling
        mask_expand = rng.random(index_mutate_children.size) < 0.6
        index_expand = index_mutate_children[mask_expand]

        if index_expand.size > 0:
            offsprings[index_expand, scale_index] += scale_step
            offsprings[index_expand, scale_index] = np.clip(offsprings[index_expand, scale_index], scale_min, scale_max)


class GeneralMutationStrategy(MutationStrategy):
    def __init__(self) -> None:
        super().__init__('General Mutation Strategy')

    #Décrémentation progressive du taux de mutation.

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()

        n_children, n_dim = offsprings.shape
        editable_dim = n_dim  # on prend en compte toutes les dimensions

        # Masque pour savoir quels enfants mutent
        mask_children = rng.random(n_children) <= mutation_rate
        index_mutate_children = np.where(mask_children)[0]

        #Si on a pas d'enfant qui mutent
        if index_mutate_children.size == 0:
            return

        # Masque pour savoir si on fait une exploration globale (True) ou locale (False)
        #70% va etre de l'exploration globale et 30% de l'exploration locale
        mask_global = rng.random(index_mutate_children.size) <= 0.7

        # Exploration Global
        index_global = index_mutate_children[mask_global]
        if index_global.size > 0:
            global_exploration(offsprings, domains, index_global, editable_dim, rng)

        #exploration local
        index_local = index_mutate_children[mask_global == False]
        if index_local.size > 0:
            local_exploration(index_local, editable_dim, offsprings, domains, rng)

class AdaptiveMutationStrategy(MutationStrategy):
    def __init__(self) -> None:
        super().__init__('Adaptive Mutation')

    #Décrémentation progressive du taux de mutation.

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        rng = np.random.default_rng()
        stds = np.std(offsprings, axis=0)
        ranges = domains.ranges[:, 1] - domains.ranges[:, 0]
        diversity = np.mean(stds / ranges)
        if diversity < 0.3:
            adaptive_rate = min(1.0, mutation_rate*2)
        else:
            adaptive_rate = mutation_rate

        mutation_multiple = 0.3
        nb_genes_mutation_max = 3

        n_dim = domains.ranges.shape[0]

        for child in offsprings:
            if rng.random() <= adaptive_rate:
                if rng.random() <= mutation_multiple:
                    nb_mutation = rng.integers(2, nb_genes_mutation_max +1)
                    genes_cible = rng.choice(n_dim, size = nb_mutation, replace = False)
                else:
                    genes_cible = [rng.integers(0, n_dim)]

                for gene in genes_cible:
                    val_min, val_max = domains.ranges[gene]
                    if rng.random() < 0.1:
                        nb_reset = rng.integers(2, nb_genes_mutation_max + 1)
                        reset_genes = rng.choice(n_dim, size=nb_reset, replace=False)
                        for gene in reset_genes:
                            val_min, val_max = domains.ranges[gene]
                            child[gene] = rng.uniform(val_min, val_max)
                            continue
                    else:
                        k = np.exp(-diversity * 5) 
                        amplitude = 0.1 * k * (val_max - val_min)

                        child[gene] += rng.normal(0, amplitude)
                        child[gene] = np.clip(child[gene], val_min, val_max)

################################################################################################# Stratégie de sélection

# class SelectGlobalParentStrategy(SelectionStrategy):
#     def __init__(self) -> None:
#         super().__init__('Select Global Parent Strategy')


