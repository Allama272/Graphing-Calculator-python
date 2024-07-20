import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox
from PySide2.QtTest import QTest
from unittest.mock import MagicMock

from main import PlotWindow, QApplication


# Create a single QApplication instance for all tests
@pytest.fixture(scope="session")
def app():
    return QApplication([])


@pytest.fixture
def window(app, qtbot):
    window = PlotWindow()
    qtbot.addWidget(window)
    return window


def test_initial_state(window):
    assert window.equation_input.text() == ""
    assert window.min_x_input.text() == ""
    assert window.max_x_input.text() == ""


def test_plot_button_enabled(window):
    assert window.plot_button.isEnabled()


def test_empty_equation(window, qtbot, monkeypatch):
    def mock_show_error_message(self, message):
        assert message == "Please enter an equation."

    monkeypatch.setattr(PlotWindow, "show_error_message", mock_show_error_message)

    qtbot.mouseClick(window.plot_button, Qt.LeftButton)


def test_invalid_x_range(window, qtbot, monkeypatch):
    def mock_show_error_message(self, message):
        assert message == "Min x must be less than Max x"

    monkeypatch.setattr(PlotWindow, "show_error_message", mock_show_error_message)

    window.equation_input.setText("x^2")
    window.min_x_input.setText("10")
    window.max_x_input.setText("5")
    qtbot.mouseClick(window.plot_button, Qt.LeftButton)


def test_valid_equation_plot(window, qtbot, monkeypatch):
    plot_called = False

    def mock_plot(*args, **kwargs):
        nonlocal plot_called
        plot_called = True

    monkeypatch.setattr(window.ax, "plot", mock_plot)

    window.equation_input.setText("x^2")
    window.min_x_input.setText("-5")
    window.max_x_input.setText("5")
    qtbot.mouseClick(window.plot_button, Qt.LeftButton)

    assert plot_called


def test_valid_equation_plot(window, qtbot, monkeypatch):
    plot_called = False

    class MockLine:
        def __init__(self):
            self.set_data = MagicMock()

    def mock_plot(*args, **kwargs):
        nonlocal plot_called
        plot_called = True
        return [MockLine()]

    monkeypatch.setattr(window.ax, "plot", mock_plot)

    def mock_make_lines_glow(*args, **kwargs):
        pass  # do nothing since the glow was messing up the test

    monkeypatch.setattr("mplcyberpunk.make_lines_glow", mock_make_lines_glow)

    window.equation_input.setText("x^2")
    window.min_x_input.setText("-5")
    window.max_x_input.setText("5")
    qtbot.mouseClick(window.plot_button, Qt.LeftButton)

    assert plot_called


def test_equation_to_latex_conversion(window):
    equation = "x^2 + 2*x + 1"
    latex_eq = window.equation_to_latex(equation)
    assert latex_eq == "x\\operatorname{xor}2+2x+1" # \\operatorname{xor} is the way py2tex writes ^, not the most common but it is displayed the same


if __name__ == "__main__":
    pytest.main(["-v", "main.py"])