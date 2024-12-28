from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont

import numpy

import time


class Stacking(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.core.register_stacking_instance(self)

       
        self.main_widget    = QWidget()
        self.main_layout    = QVBoxLayout(self.main_widget)


        stacking_label = QLabel("Stacking Options")

        font = QFont()
        font.setPointSize(20)
        stacking_label.setFont(font)

        self.main_layout.addWidget(stacking_label)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.core.get_stacking_modes())
        self.list_widget.setCurrentRow(0)

        # Tool selection list
        font = QFont()
        font.setPointSize(20)
        
        self.list_widget.setFont(font)

        self.main_layout.addWidget(self.list_widget)

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(spacer)
        

        self.slider = QSlider(Qt.Horizontal) 
        
        self.slider.setRange(1, 2)
        self.slider.setValue(1)  

        label = QLabel("Photos count : 1")
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(self.slider)

        button = QPushButton("Apply Stacking")
        self.main_layout.addWidget(button)

        self.slider.valueChanged.connect(lambda value: label.setText("Photos count : " + str(value)))

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(spacer)  
        
        button.clicked.connect(lambda: self.on_stacking_click(self.list_widget, self.slider))

        self.main_layout.addStretch()


    def get(self):
        return self.main_widget
    
    def update_range(self):
        self.slider.setRange(1, self.core.get_count() - self.core.get_curr_idx())
        self.slider.setValue(1)  
        
    def on_stacking_click(self, list_widget, slider_widget):
        row_idx       = list_widget.currentRow()
        photos_count  = slider_widget.value()

        stacking_type = list_widget.item(row_idx).text()

        print("count before add : ", self.core.get_count())
        self.core.stacking(stacking_type, photos_count)
        print("count after add : ", self.core.get_count())

    

    def on_quality_change(self, slider, label):
        quality  = slider.value()
        label.setText("Quality " + str(int(quality)))

    def on_fps_change(self, slider, label):
        quality  = slider.value()
        label.setText("Quality " + str(int(quality)))


    def on_export_image_button(self, button, extension, quality):        
        self.core.export_image(extension, quality)


    def on_export_timelapse_button(self, button, fps, quality):
        self.core.export_timelapse(fps, quality)
