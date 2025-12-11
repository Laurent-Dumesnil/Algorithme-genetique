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
import random


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy, QComboBox, QLayout, QLabel
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform, QPixmap
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF
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

class QGeometryOptimisationPanel(QSolutionToSolvePanel):
    """Panneau pour résoudre le problème de l'optimisation géométrique."""

    def __init__(self, width : int = 500, height : int = 250, points : int = 10, parent : QWidget | None = None) -> None:
        super().__init__(parent)

        self._points_scroll_bar, points_layout = create_scroll_int_value(1, points, 100)
        
        self._shapes_box = QComboBox(placeholder_text= "---- Choisissez une forme ----")
        self._shapes_box.currentTextChanged.connect(self.on_shape_text_changed)
        shapes = ["Triangle", "Rectangle", "Pentagone"]
        self._shapes_box.add_items(shapes)

        self.__width = width
        self.__height = height
        dimensions = QLabel(f'{width} x {height}')

        param_group_box = QGroupBox('Paramètres')
        param_layout = QFormLayout(param_group_box)
        param_layout.add_row('Dimensions du canevas', dimensions)
        param_layout.add_row('Nombre de points', points_layout)
        param_layout.add_row('Images', self._shapes_box)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._points_scroll_bar.valueChanged.connect(self._update_from_configuration)

        visualization_group_box = QGroupBox('Visualisation')
        visualization_group_box.alignment = Qt.AlignmentFlag.AlignCenter
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        visualization_layout = QGridLayout(visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        visualization_layout.add_widget(self._visualization_widget)
        visualization_layout.alignment = Qt.AlignmentFlag.AlignCenter

        layout = QVBoxLayout(self)
        layout.add_widget(param_group_box)
        layout.add_widget(visualization_group_box)
        
        self._background_color = QColor(48, 48, 48)
        self._points_color = QColor(255, 255, 255)   
        self._shape_color = QColor(66, 101, 235)

        self._min_translate_x = 0
        self._max_translate_x = self.__width - 0.5
        
        self._min_translate_y = 0
        self._max_translate_y = self.__height - 0.5

        self._min_rotate = 0.01
        self._max_rotate = 360
        
        self._min_scale = 1
        self._max_scale = min(self.__width, self.__height)
        
        self._max_area = self.__height * self.__width  #aire du canevas *** À Corriger avec solution optimale ***

        self._points = []

        self._chosen_shape = None

        self._transform = []
        self._best_transform = None


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
        def objective_fun(chromosome : NDArray) -> float :

            translate_x = chromosome[0]
            translate_y = chromosome[1]
            rotation = chromosome[2]
            scaling = chromosome[3]

            #center = self._chosen_shape.center()
            transform = QTransform()
            
            #translate
            transform.translate(translate_x, translate_y)

            #Rotation
            transform.rotate(rotation)
            #scale
            transform.scale(scaling, scaling)

            if len(self._transform) > 10:
                self._transform.pop(0)
            self._transform.append(transform)
            

            transformed_polygon = transform.map(self._chosen_shape)
            
            unknown_value = process_area(transformed_polygon)
            if unknown_value <= 0 or unknown_value >= self._max_area:
                return 0.0
            else:
                return int(unknown_value)
            # print(unknown_value)
        domains = Domains(np.array([[self._min_translate_x, self._max_translate_x],
                                    [self._min_translate_y, self._max_translate_y],
                                    [self._min_rotate, self._max_rotate],
                                    [self._min_scale, self._max_scale]]),
                                    ("Translation X", "Translation Y", "Rotation", "Homothétie"))
        
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
    
    def create_polygone_by_side(self, nb_side):
        center_x, center_y = 0, 0
        radius = 0.5
        num_sides = nb_side

        points = []
        for i in range(num_sides):
            angle = 2 * pi * i / num_sides + pi / 2
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            points.append(QPointF(x, y))

        self._chosen_shape = QPolygonF(points)

        return self._chosen_shape

    def on_shape_text_changed(self, text):
        if text == "Rectangle":
            self._chosen_shape = QRectF(QPointF(-0.5, -0.5), QSizeF(1, 1))
        elif text == "Triangle":
            #self._chosen_shape = QPolygonF(QPointF(0, -0.5), QPointF(-0.5, 0.5), QPointF(0.5, 0.5))
            self._chosen_shape = self.create_polygone_by_side(3)
        else :
           self._chosen_shape = self.create_polygone_by_side(5)

        return self._chosen_shape
    
    def _create_points(self):
        self._points = []
        for _ in range(self._points_scroll_bar.value):
            self._points.append(QPointF(random.uniform(0, self.__width), random.uniform(0, self.__height)))

    def _draw_points(self, painter : QPainter) -> None:
        """Dessine les points."""

        painter.save()

        pen = QPen()
        pen.set_color(self._points_color)
        pen.set_width(2)

        painter.set_pen(pen)
        painter.set_brush(self._points_color)

        painter.draw_points(self._points)

        painter.restore()

    def _draw_rectangle(self, painter : QPainter, transform : QTransform, fill : bool):
        """Dessine un rectangle"""

        painter.save()

        if not fill:
            pen = QPen()
            pen.set_color(self._shape_color)
            pen.set_width(2)
            painter.set_pen(pen)
            painter.set_brush(Qt.NoBrush)
        else:
            painter.set_pen(Qt.NoPen)
            painter.set_brush(self._shape_color)

        # painter.set_transform(transform)

        shape = transform.map(self._chosen_shape)
        painter.draw_polygon(shape)

        painter.restore()
    
    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:  
        image = QPixmap(QSize(self.__width, self.__height))
        image.fill(self._background_color)
        painter = QPainter(image)
        painter.set_pen(Qt.NoPen)

        self._draw_points(painter)

        if ga:
            for transform in self._transform:
                self._draw_rectangle(painter, transform, False)

        painter.end()
        self._visualization_widget.image = image.to_image()

    @Slot()
    def _update_from_configuration(self):
        """Met à jour la visualisation de la boîte en fonction de la configuration."""
        self._create_points()
        self._update_from_simulation(None)
