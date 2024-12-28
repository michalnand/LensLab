from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont

import numpy

import time

class Export(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.core.register_export_instance(self)

       
        self.main_widget    = QWidget()
        self.main_layout    = QVBoxLayout(self.main_widget)


        # quality settings
        self.quality_label = QLabel("Quality 98")
        self.main_layout.addWidget(self.quality_label)   


        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(int(5), int(100))
        self.quality_slider.setValue(int(98))
        self.main_layout.addWidget(self.quality_slider)   

        self.quality_slider.valueChanged.connect(lambda : self.on_quality_change(self.quality_slider, self.quality_label))

        # spacing
        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(spacer)
        
        # image export mode
        self.button_jpg = QPushButton("Export image JPG")
        self.main_layout.addWidget(self.button_jpg)  

        
        self.button_jpg.clicked.connect(lambda : self.on_export_image_button(self.button_jpg, "jpg", self.quality_slider.value()))

        self.button_png = QPushButton("Export image PNG")    
        self.main_layout.addWidget(self.button_png)
        self.button_png.clicked.connect(lambda : self.on_export_image_button(self.button_png, "png", self.quality_slider.value()))

        # spacing
        self.spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(self.spacer)

        # timelapse export
        self.timelapse_label = QLabel("Timelapse")

        font = QFont()
        font.setPointSize(20)
        self.timelapse_label.setFont(font)

        self.main_layout.addWidget(self.timelapse_label) 


        self.fps_label = QLabel("FPS 25")
        self.main_layout.addWidget(self.fps_label) 

        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(int(10), int(60))
        self.fps_slider.setValue(int(25))
        self.main_layout.addWidget(self.fps_slider) 

        self.fps_slider.valueChanged.connect(lambda : self.on_fps_change(self.fps_slider, self.fps_label))

        button_timelapse = QPushButton("Export timelapse")
        self.main_layout.addWidget(button_timelapse)
        button_timelapse.clicked.connect(lambda: self.on_export_timelapse_button(button_timelapse, self.fps_slider.value(), self.quality_slider.value()))


        self.main_layout.addStretch()

    def get(self):
        return self.main_widget
    

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
