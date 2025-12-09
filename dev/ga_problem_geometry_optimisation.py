#    ____   _____                           _               ____        _   _           _           _   _             _____                 _ 
#   / __ \ / ____|                         | |             / __ \      | | (_)         (_)         | | (_)           |  __ \               | |
#  | |  | | |  __  ___  ___  _ __ ___   ___| |_ _ __ _   _| |  | |_ __ | |_ _ _ __ ___  _ ___  __ _| |_ _  ___  _ __ | |__) |_ _ _ __   ___| |
#  | |  | | | |_ |/ _ \/ _ \| '_ ` _ \ / _ \ __| '__| | | | |  | | '_ \| __| | '_ ` _ \| / __|/ _` | __| |/ _ \| '_ \|  ___/ _` | '_ \ / _ \ |
#  | |__| | |__| |  __/ (_) | | | | | |  __/ |_| |  | |_| | |__| | |_) | |_| | | | | | | \__ \ (_| | |_| | (_) | | | | |  | (_| | | | |  __/ |
#   \___\_\\_____|\___|\___/|_| |_| |_|\___|\__|_|   \__, |\____/| .__/ \__|_|_| |_| |_|_|___/\__,_|\__|_|\___/|_| |_|_|   \__,_|_| |_|\___|_|
#                                                     __/ |      | |                                                                          
#                                                    |___/       |_|                                                                                     
# -----------------------------------------
# Classes servant à afficher et résoudre le problème de l'optimisation géométrique
# -----------------------------------------
# Auteurs :
# Laurent Dumesnil
# Julien Lamontagne
# Guillaume Foisy
# Eduardo Eugenio Gomez Torres
# -----------------------------------------
# date : 8 décembre 2025
# -----------------------------------------


import numpy as np
from numpy.typing import NDArray


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy, QComboBox, QLayout
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF

# -----------------------------------------------------------------------------
from shibokensupport import feature # type: ignore[import-not-found]
feature.set_selection(feature.snake_case | feature.true_property)
assert "snake_case" in feature.info() and "true_property" in feature.info()
# -----------------------------------------------------------------------------

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtwidgets import QImageViewer, create_scroll_real_value, create_scroll_int_value

class QGeometryOptimisationPanel(QSolutionToSolvePanel):
    """Panneau pour résoudre le problème de l'optimisation géométrique."""

    def __init__(self, width : int = 10., height : int = 5., points : int = 10, parent : QWidget | None = None) -> None:
        super().__init__(parent)

        self._width_scroll_bar, width_layout = create_scroll_real_value(0.1, width, 10., 1, value_suffix = ' m')
        self._height_scroll_bar, height_layout = create_scroll_real_value(0.1, height, 10., 1, value_suffix = ' m')
        self._points_scroll_bar, points_layout = create_scroll_int_value(1, points, 100)
        
        self._shapes_box = QComboBox(placeholder_text= "---- Choisissez une forme ----")
        shapes = ["Triangle", "Rectangle", "Pentagone"]
        self._shapes_box.add_items(shapes)
        # shape_layout = QLayout()
        # shape_layout.add_widget(self._shapes_box)

        param_group_box = QGroupBox('Paramètres')
        param_layout = QFormLayout(param_group_box)
        param_layout.add_row('Largeur du canevas', width_layout)
        param_layout.add_row('Hauteur du canevas', height_layout)
        param_layout.add_row('Nombre de points', points_layout)
        param_layout.add_row('Images', self._shapes_box)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._width_scroll_bar.valueChanged.connect(self._update_from_configuration)
        self._height_scroll_bar.valueChanged.connect(self._update_from_configuration)
        self._points_scroll_bar.valueChanged.connect(self._update_from_configuration)

        visualization_group_box = QGroupBox('Visualisation')
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        visualization_layout = QGridLayout(visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        visualization_layout.add_widget(self._visualization_widget)

        layout = QVBoxLayout(self)
        layout.add_widget(param_group_box)
        layout.add_widget(visualization_group_box)
        
        self._background_color = QColor(48, 48, 48)
        self._box_color = QColor(148, 164, 222)
        self._box_visualization_ratio = 0.9     

    @property
    def name(self) -> str:
        """Retourne le nom du problème."""
        return 'Optimisation géométrique'

    @property
    def summary(self) -> str:
        """Retourne un résumé du problème."""
        return '''Le problème de l'optimisation géométrique consiste à placer une forme donnée dans son plus grand format sur un canevas, sans toucher les obstacles.'''

    @property
    def description(self) -> str:
        """Retourne une description détaillée du problème."""
        return '''On cherche à trouver la taille de la plus grande forme qui peut être placée sur ce canevas sans toucher aux points. Il est permis de faire des manipulations de translations horizontales et verticales, de rotations et d'homothétie.''' 


    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:  
        pass 

    @Slot()
    def _update_from_configuration(self):
        """Met à jour la visualisation de la boîte en fonction de la configuration."""
        self._update_from_simulation(None)
