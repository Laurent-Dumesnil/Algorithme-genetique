
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
import random, math


# -----------------------------------------------------------------------------
import PySide6 
from __feature__ import snake_case, true_property # type: ignore[import-not-found]
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy, QComboBox, QLayout, QLabel, QPushButton
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform, QPixmap
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF, QRect, QPoint, QMargins, QObject
from PySide6.QtCharts import QChart, QSplineSeries, QValueAxis, QChartView
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

    def __init__(self, width : int = 500, height : int = 250, notes: int = 1 , octave: int = -1, volume : int = 1, parent : QWidget | None = None)-> None:
        super().__init__(parent)

        self._notes_scroll_bar, notes_layout = create_scroll_int_value(1, notes, 10)
        self._octave_scroll_bar, octave_layout = create_scroll_int_value(-1, octave, 9)
        self._amplitude_scroll_bar, amplitude_layout = create_scroll_int_value(-1, volume, 1)

        self.__width = width
        self.__height = height

        self._duration = 1.0 # durée du son (en secondes)
        self._sampling_rate = 100 # nombre de fois qu'un signal sonore est mesuré par seconde.
        
        self._reference_amplitude = 0.8 # amplitude recherché (de la courbe de référence)
        self._reference_frequency = 420 # fréquence recherché (de la courbe de référence)

        param_group_box = QGroupBox('Paramètres')
        param_layout = QFormLayout(param_group_box)
        param_layout.add_row('Nombre de notes', notes_layout)
        param_layout.add_row('Octave', octave_layout)
        param_layout.add_row('Amplitude', amplitude_layout)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._notes_scroll_bar.valueChanged.connect(self._update_from_configuration)
        self._octave_scroll_bar.valueChanged.connect(self._update_button)

        keyboard_group_box = QGroupBox('Keyboard')
        keyboard_group_box.alignment = Qt.AlignmentFlag.AlignCenter
        keyboard_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        keyboard_layout = QGridLayout(keyboard_group_box)
        
        keyboard_container = self._create_keyboard()
        keyboard_layout.add_widget(keyboard_container)
        keyboard_layout.alignment = Qt.AlignmentFlag.AlignCenter

        self._notes = []
        self._solution = None

        visualization_group_box = QGroupBox('Visualisation')
        visualization_group_box.alignment = Qt.AlignmentFlag.AlignCenter
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._visualization_layout = QGridLayout(visualization_group_box)
        # self._visualization_widget = QImageViewer(True)
        # self._visualization_layout.add_widget(self._visualization_widget)
        chart = self._create_chart()
        self._view = QChartView(chart)
        self._view.set_fixed_height(200)
        self._visualization_layout.add_widget(self._view)
        self._visualization_layout.alignment = Qt.AlignmentFlag.AlignCenter

        layout = QVBoxLayout(self)
        layout.add_widget(param_group_box)
        layout.add_widget(keyboard_group_box)
        layout.add_widget(visualization_group_box)

        self._background_color = QColor(48, 48, 48)
        self._solution_color = QColor(76, 175, 80)
        self._population_color = QColor(2, 119, 189)
        self._best_color = QColor(255, 143, 0)

        self._num_curve_points = int(self._duration * self._sampling_rate) # nombre de points choisi sur la courbe selon la durée du son
        self._t_on_curve = np.linspace(0, self._duration, self._num_curve_points) # retourne un array des points sur la courbe (temps de référence à comparer)
        self._reference_curve = (self._reference_amplitude * np.sin(2 * np.pi * self._reference_frequency * self._t_on_curve)) # la courbe de référence utilisant la formule de sinus => x = A*sin(F*t)
        

    def reference_curve_constructor(self):
        pass

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
            
            amplitude = chromosome[0]
            frequency = chromosome[1]

            current_iteration_curve = amplitude * np.sin(2 * np.pi * frequency * self._t_on_curve)

            dist_between_curves = np.mean((self._reference_curve - current_iteration_curve)**2)

            return 1.0 / (1.0 + dist_between_curves)


        domains = Domains(
            np.array([[-1.0, 1.0],
                      [20.0, 20000.0]]),
                      ("Amplitude", "Fréquence")
        )

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
    
    def _update_from_simulation(self, ga):
        pass
    
    @Slot()
    def _update_from_configuration(self):
        """Met à jour la visualisation de la boîte en fonction de la configuration."""
        chart = self._create_chart()
        self._visualization_layout
        self._visualization_layout.remove_widget(self._view)
        self._view = QChartView(chart)
        self._view.set_fixed_height(200)
        self._visualization_layout.add_widget(self._view)
        pass

    def _create_points(self):
        x_total = np.zeros((1000))
        y_total = np.zeros((1000))
        for n in self._notes:
            a = n[1]
            f = n[0]
            x = np.linspace(0., 1., 1000)
            y = a * np.sin(2 * np.pi * f * x) 
            x_total += x
            y_total += y
        return (x_total, y_total)

    def _create_chart(self):
        chart = QChart()
        line = QSplineSeries()
        # value = QValueAxis()
        x, y = self._create_points()
        line.append_np(x, y)
        chart.add_series(line)

        return chart
        
    
    def _update_button(self):
        for btn in self._buttons.values():
            btn.octave = self._octave_scroll_bar.value

    def _key_pressed(self, key):
        btn = self._buttons[key]
        if len(self._notes) >= self._notes_scroll_bar.value:
            self._notes.pop(0)
        self._notes.append((btn.value, self._amplitude_scroll_bar.value))
        self._update_from_configuration()

    def _create_keyboard(self):
        """Nous avons utilisé ChatGPT pour générer un petit exemple sur lequel on s'est basé pour approcher deux problématiques
        dans le code qui suit. C'est-à-dire l'utilisation du style_sheet pour la stylisation des widgets et la superposition de
        deux layouts afin d'avoir les touches noires qui chevauchent les touches blanches."""
        keyboard_container = QWidget()
        keyboard_container.set_fixed_height(160)
        keyboard_container.set_fixed_width(425)
        keyboard_container.style_sheet = "background: transparent"

        white_layout = QHBoxLayout(keyboard_container)
        white_layout.spacing = 2
        white_keys = ["C", "D", "E", "F", "G", "A", "B"]
        self._buttons = {}

        for key in white_keys:
            btn = KeyboardButton(key, self._octave_scroll_bar.value)
            btn.set_fixed_size(50, 120)
            btn.clicked.connect(lambda _, k = key : self._key_pressed(k))
            btn.style_sheet= """
            QPushButton {
                background: white;
                border: 1px solid;
                text-align: bottom;
                padding-bottom: 4px;
            }
            QPushButton:pressed {
                background: #ddd;
            }
            """
            self._buttons[key] = btn
            white_layout.add_widget(btn)

        black_container = QWidget(keyboard_container)
        black_container.geometry = QRect(0, 0, 500, 100)
        black_keys = [("C#", 45), ("D#", 105), ("F#", 220), ("G#", 275), ("A#", 335)]
        self._black_buttons = {}
        
        for key, x in black_keys:
            btn = KeyboardButton(key, self._octave_scroll_bar.value, black_container)
            btn.set_fixed_size(40, 80)
            btn.move(x, 0)
            btn.clicked.connect(lambda _, k = key : self._key_pressed(k))
            btn.style_sheet= """
            QPushButton {
                background: black;
                color : white;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background: #444;
            }
            """
            self._buttons[key] = btn
            btn.raise_()

        return keyboard_container


class KeyboardButton(QPushButton):
    _frequency = {
        "C" : 16.3516015625,
        "C#" : 17.32390625,
        "D" : 18.3540625,
        "D#" : 19.4454296875,
        "E" : 20.60171875,
        "F" : 21.8267578125,
        "F#" : 23.1246484375,
        "G" : 24.4997265625,
        "G#" : 25.9565625,
        "A": 27.5,
        "A#" : 29.135234375,
        "B" : 30.8676953125
    }

    def __init__(self, key, octave, parent = None):
        super().__init__(key, parent)
        self._key = key
        self._octave = octave
        self._value = KeyboardButton._frequency[key] * math.pow(2, octave + 1)
        pass

    @property
    def key(self):
        return self._key
    
    @property
    def value(self):
        return self._value 
    
    @property
    def octave(self):
        return self._octave
    
    @octave.setter
    def octave(self, value : int):
        self._octave = value
        self._value = KeyboardButton._frequency[self._key] * math.pow(2, self._octave + 2)