
# -----------------------------------------
# Classes servant à afficher et résoudre le problème de trouver le signal sinusoïdal de notes choisies
# -----------------------------------------
# Auteurs :
# Laurent Dumesnil
# Julien Lamontagne
# Guillaume Foisy
# Eduardo Eugenio Gomez Torres
# -----------------------------------------
# date : 16 décembre 2025
# -----------------------------------------


import numpy as np
from numpy.typing import NDArray
import random


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy, QComboBox, QLayout, QLabel
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform, QPixmap
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF, QRect, QPoint
from math import pi, cos, sin

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtwidgets import QImageViewer, create_scroll_real_value, create_scroll_int_value
from uqtgui import process_area


class QSoundWaveFinderPanel(QSolutionToSolvePanel):
    """Panneau pour resoudre le problème de trouver le signal sinusoïdal qui est produit par les notes choisies."""

    def __init__(self, width : int = 500, height : int = 250, notes: int = 1 , parent : QWidget | None = None)-> None:
        super().__init__(parent)

        self._points_scroll_bar, notes_layout = create_scroll_int_value(1, notes, 100)

        self.__width = width
        self.__height = height

        param_group_box = QGroupBox('Paramètres')
        param_layout = QFormLayout(param_group_box)
        param_layout.add_row('Nombre de notes', notes_layout)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        visualization_group_box = QGroupBox('Visualisation')
        visualization_group_box.alignment = Qt.AlignmentFlag.AlignCenter
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        visualization_layout = QGridLayout(visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        visualization_layout.add_widget(self._visualization_widget)
        visualization_layout.alignment = Qt.AlignmentFlag.AlignCenter

    @property
    def name(self) -> str:
        """Retourne le nom du problème."""
        return 'Trouver signal sinusoïdal des notes'

    @property
    def summary(self) -> str:
        """Retourne un résumé du problème."""
        return '''Le problème consiste à trouver le signal sinusoïdale qui est produit selon les notes choisies'''

    @property
    def description(self) -> str:
        """Retourne une description détaillée du problème."""
        return '''On cherche à trouver une  '''
    @property
    def width(self):
        """Retourne la largeur du canevas."""
        return self.__width()
    
    @property
    def height(self):
        """Retourne la hauteur du canevas"""
        return self.__height()
    
    @property
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        
        La définition du problème inclue les domaines des chromosomes et la fonction objective.
        """
        def objective_fun(chromosome :NDArray) -> float:
            pass

        domains = Domains()

        return ProblemDefinition(domains, objective_fun)
    
    @property
    def default_parameters(self) -> Parameters:
        """Retourne les paramètres par défaut de l'algorithme génétique.
        
        Ces paramètres sont utilisés pour initialiser les paramètres de l'interface graphique 
        et remplace ceux en place.
        """
        engine_parameters = Parameters()
        engine_parameters.maximum_epoch = 100
        engine_parameters.population_size = 20
        engine_parameters.elitism_rate = 0.1
        engine_parameters.selection_rate = 0.75
        engine_parameters.mutation_rate = 0.25
        return engine_parameters
    
    @Slot()
    def _update_from_configuration(self):
        """Met à jour la visualisation de la boîte en fonction de la configuration."""
        pass