#   ____    _                      _       
#  / ___|  / \     _ __ ___   __ _(_)_ __  
# | |  _  / _ \   | '_ ` _ \ / _` | | '_ \ 
# | |_| |/ ___ \  | | | | | | (_| | | | | |
#  \____/_/   \_\ |_| |_| |_|\__,_|_|_| |_|
#                                          
# -----------------------------------------
# Démarrage de l'application principale
# -----------------------------------------


import sys



# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QApplication

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------


from gaapp import QGAApp

from ga_strategy_genes_mutation import GenesMutationStrategy
from ga_problem_unknown_number import QUnknownNumberProblemPanel
from ga_problem_open_box import QOpenBoxProblemPanel




def main():
    # 1) Instanciation de l'engin Qt
    # -----------------------------------------------
    app = QApplication(sys.argv)

    # 2) Instanciation de l'application
    # -----------------------------------------------
    ga_app = QGAApp()

    # 3) Ajout de stratégies : sélection, croisement, mutation, ...
    # -----------------------------------------------
    # Note : par défaut, l'algorithme possède une stratégie par défaut pour chaque étape fondamentale
    # -----------------------------------------------
    # ga_app.add_selection_strategy(...)
    # ga_app.add_crossover_strategy(...)
    # ga_app.add_mutation_strategy(...)
    # -----------------------------------------------
    # Exemple : ajout d'une stratégie de mutation
    ga_app.add_mutation_strategy(GenesMutationStrategy)                             # note : on passe une classe, pas une instance

    # 4) Ajout des panneaux de résolution de problème
    # -----------------------------------------------
    # Note : par défaut, le logiciel ne possède aucun panneau de résolution de problème
    # IMPORTANT : il faut au moins un panneau pour pouvoir résoudre un problème
    # -----------------------------------------------
    # Exemple : ajout de deux panneaux de résolution de problème
    # -----------------------------------------------
    # Problème du nombre inconnu
    ga_app.add_solution_panel(QUnknownNumberProblemPanel(-1000.0, 0.0, 1000.0))    # note : on passe une instance, pas une classe
    # Problème de la boîte ouverte
    ga_app.add_solution_panel(QOpenBoxProblemPanel())                              # note : on passe une instance, pas une classe

    # 5) Affichage et exécution de l'application
    # -----------------------------------------------
    ga_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

