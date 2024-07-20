import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QMessageBox, QLabel
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
import mplcyberpunk
from pytexit import py2tex

class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphical Calculator")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("calc_icon.png"))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Equation input
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("Enter an equation in terms of x")
        main_layout.addWidget(self.equation_input)

        # X range inputs
        range_layout = QHBoxLayout()
        main_layout.addLayout(range_layout)

        self.min_x_input = QLineEdit()
        self.min_x_input.setPlaceholderText("Min x")
        self.min_x_input.setFixedWidth(100)
        range_layout.addWidget(self.min_x_input)

        range_layout.addWidget(QLabel("to"))

        self.max_x_input = QLineEdit()
        self.max_x_input.setPlaceholderText("Max x")
        self.max_x_input.setFixedWidth(100)
        range_layout.addWidget(self.max_x_input)

        range_layout.addStretch()

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_equation)
        self.plot_button.setCursor(Qt.PointingHandCursor)
        self.plot_button.setShortcut("Return")
        main_layout.addWidget(self.plot_button)

        # Matplotlib canvas
        plt.style.use("cyberpunk")
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # replace dict
        self.func_to_np = {
            '^': '**',
            'sqrt': 'np.sqrt',
            'log10': 'np.log10',
            'ln': 'np.log',
            'log2': 'np.log2',
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan'
        }

        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                font-size: 20px;
            }
            QPushButton {
                background-color: #4A90E2;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
            QPushButton:pressed {
                background-color: #3A80D2;
            }
            QLabel {
                font-size: 23px;
            }
            
            QTabWidget
            {
                background:#3A80D2
            }
        """)

    def fix_equation(self, equation):
        equation = equation.lower()
        for word, replacement in self.func_to_np.items():
            equation = equation.replace(word, replacement)
        return equation

    def evaluate(self, x, equation):
        return eval(equation)

    def equation_to_latex(self, equation):
        latex_equation = py2tex(equation, print_latex=False, print_formula=False)
        latex_equation = latex_equation.replace("$", "")
        latex_equation = latex_equation.replace("log2", "log_{2}")
        return latex_equation

    def plot_equation(self):
        equation = self.equation_input.text()

        if not equation:
            self.show_error_message("Please enter an equation.")
            return

        try:
            x_min = float(self.min_x_input.text() or "-10")
            x_max = float(self.max_x_input.text() or "10")
            if x_min >= x_max:
                raise ValueError("Min x must be less than Max x")
        except ValueError as e:
            self.show_error_message(str(e))
            return

        equation = self.fix_equation(equation)
        num_points = int((x_max - x_min) * 100) # to ensure that the plot is always smooth no matter the size of the plot
        x = np.linspace(x_min, x_max, num_points)
        try:
            y = self.evaluate(x, equation)
        except Exception as e:
            self.show_error_message(f"Error evaluating the equation: {str(e)}\n"
                                    "Use Valid operators, for example: 3x is wrong, while 3*x is correct.")
            return

        try:
            latex_eq = self.equation_to_latex(equation)
        except ValueError as e:
            self.show_error_message(f"{str(e)} \n can't convert to Latex")
            latex_eq = equation  # Fall back to original equation if LaTeX conversion fails

        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_title(f"$y = {latex_eq}$", fontsize=16)
        self.ax.set_xlabel('x', fontsize=15)
        self.ax.set_ylabel('y', fontsize=15)
        self.ax.grid(True)
        self.ax.axhline(y=0, color='k', linestyle='--')
        self.ax.axvline(x=0, color='k', linestyle='--')
        mplcyberpunk.make_lines_glow(self.ax)

        self.canvas.draw()

    def show_error_message(self, message):
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setText("Error")
        error_box.setInformativeText(message)
        error_box.setWindowTitle("Input Error")
        error_box.setStyleSheet("""
               QMessageBox {
                   background-color: #2E2E2E;
                   color: #FFFFFF;
               }
               QMessageBox QLabel {
                   color: #FFFFFF;
               }
               QPushButton {
                   background-color: #4A90E2;
                   border: none;
                   padding: 5px 15px;
                   border-radius: 3px;
                   font-size: 12px;
                   color: #FFFFFF;
               }
               QPushButton:hover {
                   background-color: #5AA0F2;
               }
           """)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setDefaultButton(QMessageBox.Ok)
        error_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())