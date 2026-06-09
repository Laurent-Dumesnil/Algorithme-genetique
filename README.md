# GAEngine — Algorithme Génétique avec interface PySide6

Projet scolaire d'optimisation par algorithme génétique modulaire avec interface graphique PySide6.

L'application permet de résoudre différents problèmes d'optimisation (boîte ouverte, optimisation géométrique, recherche de nombre inconnu, reconstruction d'onde sonore) en évoluant une population de chromosomes selon des stratégies de sélection, croisement et mutation configurables.

---

## Technologies utilisées

`Python` · `NumPy` · `PySide6` · `Qt 6`

---

## Architecture du projet

Le projet suit une architecture en couches avec abstraction complète de l'algorithme génétique :

```
gacvm (moteur GA)
    ├── Domains             ← Définition des espaces de recherche par dimension
    ├── ProblemDefinition   ← Encapsulation domaines + fonction objective
    ├── Parameters          ← Hyperparamètres (population, epochs, taux...)
    └── GeneticAlgorithm    ← Moteur d'évolution (sélection, croisement, mutation)

gaapp (interface)
    └── QGAApp                          ← Fenêtre principale, registre des stratégies et panneaux
            └── QSolutionToSolvePanel   ← Interface abstraite pour chaque problème

Problèmes (panels concrets)
    ├── QOpenBoxProblemPanel          ← Maximisation du volume d'une boîte ouverte
    ├── QGeometryOptimisationPanel    ← Plus grande forme sans toucher les obstacles
    ├── QUnknownNumberProblemPanel    ← Recherche d'un nombre cible
    └── QSoundWaveFinderPanel         ← Reconstruction d'une onde sonore

Stratégies de mutation
    ├── GenesMutationStrategy         ← Réinitialisation totale aléatoire
    ├── GeometryMutationStrategy      ← Optimisée pour les transformations géométriques
    ├── GeneralMutationStrategy       ← 90% globale / 10% locale
    ├── ExploitativeMutationStrategy  ← Mutation locale guidée par la diversité
    ├── MixedMutationStrategy         ← Hybride avec réinitialisation partielle (10%)
    └── AdaptiveMutationStrategies    ← Sélection probabiliste entre stratégies
```

---

## Fonctionnalités

**Moteur génétique modulaire :**

- Domaines de recherche multidimensionnels avec bornes par gène
- Stratégies de sélection, croisement et mutation interchangeables à l'exécution
- Historique complet de l'évolution (meilleure solution, fitness par époque)
- Élitisme configurable pour préserver les meilleures solutions

**Stratégies de mutation :**

| Stratégie | Description |
|---|---|
| `GenesMutationStrategy` | Réinitialise tous les gènes d'un individu aléatoirement |
| `GeometryMutationStrategy` | 70% exploration globale / 30% locale + scaling progressif |
| `GeneralMutationStrategy` | 90% exploration globale / 10% locale vectorisée |
| `ExploitativeMutationStrategy` | Amplitude réduite dynamiquement selon la diversité de la population |
| `MixedMutationStrategy` | Exploitative avec 10% de chance de réinitialisation partielle |
| `AdaptiveMutationStrategies` | Sélection probabiliste : 45% General / 50% Exploitative / 5% Genes |

**Problèmes inclus :**

- **Boîte ouverte** — Trouver la taille de découpe maximisant le volume `(w-2c)(h-2c)c`
- **Optimisation géométrique** — Placer la plus grande forme (triangle, rectangle, pentagone) sur un canevas sans toucher les obstacles, avec translation, rotation et homothétie
- **Nombre inconnu** — Converger vers une valeur cible dans un domaine configurable
- **Onde sonore** — Reconstruire les paramètres d'une onde à partir de sa forme

**Interface graphique :**

- Ajout dynamique de stratégies et de problèmes via `QGAApp`
- Visualisation en temps réel de la population et de la meilleure solution
- Paramètres configurables (population, epochs, taux d'élitisme, sélection, mutation)
- Panneaux interactifs avec scrollbars pour ajuster les données du problème

---

## Installation

**Prérequis :** Python 3.11+

```bash
git clone https://github.com/Laurent-Dumesnil/Algorithme-genetique
cd Algorithme-genetique

pip install numpy PySide6
```

---

## Utilisation

### Lancer l'interface graphique

```bash
python gamain.py
```

1. Sélectionner un **problème** dans la liste des panneaux disponibles
2. Choisir une **stratégie de mutation** dans le menu déroulant
3. Configurer les **paramètres** (taille de population, nombre d'époques, taux de mutation...)
4. Cliquer **Start** pour lancer l'évolution et observer la population converger en temps réel
5. Consulter l'historique pour analyser la progression de la fitness

### Ajouter un nouveau problème

Créer une classe héritant de `QSolutionToSolvePanel` et implémenter :

```python
class MonProbleme(QSolutionToSolvePanel):
    @property
    def problem_definition(self) -> ProblemDefinition:
        domains = Domains(np.array([[min1, max1], [min2, max2]]), ('Gène 1', 'Gène 2'))
        return ProblemDefinition(domains, ma_fonction_objective)

    @property
    def default_parameters(self) -> Parameters:
        p = Parameters()
        p.maximum_epoch = 100
        p.population_size = 20
        return p
```

Puis l'enregistrer dans `gamain.py` :

```python
ga_app.add_solution_panel(MonProbleme())
```

### Ajouter une stratégie de mutation

Créer une classe héritant de `MutationStrategy` :

```python
class MaStrategie(MutationStrategy):
    def __init__(self):
        super().__init__('Ma Stratégie')

    def mutate(self, offsprings: NDArray, mutation_rate: float, domains: Domains) -> None:
        # logique de mutation
        ...
```

Puis l'enregistrer dans `gamain.py` :

```python
ga_app.add_mutation_strategy(MaStrategie)  # passer la classe, pas une instance
```

---

## Performances

| Problème | Résultat typique |
|---|---|
| Boîte ouverte (10×5) | Converge vers l'optimum analytique en < 50 époques |
| Optimisation géométrique | Trouve une grande forme en évitant tous les obstacles |
| Nombre inconnu | Convergence quasi-immédiate |
| Onde sonore | Reconstruction fidèle en quelques centaines d'époques |

---

## Structure du projet

```
├── gamain.py                         # Point d'entrée — configuration et lancement
├── gaapp.py                          # Fenêtre principale QGAApp et QSolutionToSolvePanel
├── gacvm.py                          # Moteur GA : Domains, ProblemDefinition, GeneticAlgorithm
│
├── ga_problem_open_box.py            # Problème de la boîte ouverte
├── ga_problem_geometry_optimisation.py # Problème d'optimisation géométrique
├── ga_problem_unknown_number.py      # Problème du nombre inconnu
├── ga_problem_sound_wave_finder.py   # Problème de reconstruction d'onde sonore
│
├── ga_strategy_genes_mutation.py     # Stratégie de mutation par réinitialisation complète
├── ga_custom_strategy.py             # Stratégies : Geometry, General, Exploitative, Mixed
├── ga_adaptiveMS.py                  # Stratégie adaptative (sélection probabiliste)
│
├── uqtwidgets.py                     # Widgets Qt utilitaires (QImageViewer, scrollbars)
├── uqtgui.py                         # Utilitaires géométriques Qt (aire, périmètre)
└── umath.py                          # Utilitaires mathématiques (clamp)
```

---

## Ce que j'ai appris

Ce projet m'a permis de mettre en pratique la conception d'un moteur générique d'algorithme génétique entièrement découplé des problèmes qu'il résout. La partie la plus intéressante a été la conception des stratégies de mutation adaptatives — notamment l'idée d'utiliser la diversité de la population (écart-type / étendue) pour ajuster dynamiquement l'amplitude des mutations et éviter la convergence prématurée.

La stratégie `AdaptiveMutationStrategies` illustre bien ce principe : plutôt que de choisir une seule approche de mutation, elle sélectionne probabilistiquement entre exploration globale et exploitation locale à chaque génération, ce qui améliore la robustesse sur des espaces de recherche variés.
