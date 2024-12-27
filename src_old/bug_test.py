import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton,
    QSlider)
from PyQt5.QtCore import Qt

import numpy, random, string

from TabButtons import *

class RandomWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        for n in range(1, 5):
            label_name = ''.join(random.choices(string.ascii_letters, k=7))
            label = QLabel(label_name)
            self.layout.addWidget(label)

            min_value  = 0
            max_value  = 100
            curr_value = numpy.random.randint(0, 100)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_value, max_value)
            slider.setValue(curr_value)
            self.layout.addWidget(slider)

            # Connect slider A to its handler
            slider.valueChanged.connect(lambda _, slider_=slider, label_=label, label_name_=label_name: self._on_slider_change(slider_, label_, label_name_))

    def get(self):
        return self.widget
    
    def _on_slider_change(self, slider, label, label_name):
        value = slider.value()
        label.setText(label_name + " " + str(value))

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("App Test")
        self.setGeometry(100, 100, 500, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        tab_buttons = TabButtons()

        w1 = RandomWidget()
        w2 = RandomWidget()
        w3 = RandomWidget()

        tab_buttons.add("tools", w1.get())
        tab_buttons.add("options", w2.get())
        tab_buttons.add("exit", w3.get())
        

        self.main_layout.addWidget(tab_buttons.get())

        
        self.main_layout.addStretch()


        
        
    def _make_tool_box_widget(self):
        # Create a new widget to contain the layout
        tool_box_widget = QWidget()

        # Create a layout for the widget
        tool_box_layout = QVBoxLayout()

        # Slider A
        label_a = QLabel("Text A")
        tool_box_layout.addWidget(label_a)

        slider_a = QSlider(Qt.Horizontal)
        slider_a.setRange(0, 100)
        slider_a.setValue(20)
        tool_box_layout.addWidget(slider_a)

        # Connect slider A to its handler
        slider_a.valueChanged.connect(lambda: self.on_slider_a_change(slider_a, label_a))

        # Slider B
        label_b = QLabel("Text B")
        tool_box_layout.addWidget(label_b)

        slider_b = QSlider(Qt.Horizontal)
        slider_b.setRange(0, 100)
        slider_b.setValue(20)
        tool_box_layout.addWidget(slider_b)

        # Connect slider B to its handler
        slider_b.valueChanged.connect(lambda: self.on_slider_b_change(slider_b, label_b))

        # Set the layout for the tool_box_widget
        tool_box_widget.setLayout(tool_box_layout)

        return tool_box_widget

    def on_slider_a_change(self, slider, label):
        # Update label A text with the value of slider A
        value = slider.value() / 10.0
        label.setText(f"Text A {value}")

      
    def on_slider_b_change(self, slider, label):
        # Update label B text with the value of slider B
        value = slider.value() / 10.0
        label.setText(f"Text B {value}")

   
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main = TestApp()
    app_main.show()
    sys.exit(app.exec_())

