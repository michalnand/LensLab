from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QListWidget,
                             QSlider, QLabel, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg

import sys
import numpy

    
class Tools(QWidget):
    def __init__(self, core):
        super().__init__()

        self.n_steps = 64
        self.core = core

        self.core.register_tools_instance(self)

        self.main_widget    = QWidget()
        self.main_layout    = QVBoxLayout(self.main_widget)


        # Histogram section
        self.histogram_widget = pg.PlotWidget()
        self.histogram_widget.setTitle("Histogram")
        self.histogram_widget.setLabel("left", "Frequency")
        self.histogram_widget.setLabel("bottom", "Pixel Intensity")
        self.main_layout.addWidget(self.histogram_widget, stretch=1)

        # Tool selection list
        self.tool_list = QListWidget()
        font = QFont()
        font.setPointSize(20)
        
        self.tool_list.setFont(font)

        tool_names = self.core.get_tool_names()


        self.tool_list.addItems(tool_names)
        self.tool_list.currentItemChanged.connect(self.on_tool_selected)   
        self.main_layout.addWidget(self.tool_list, stretch=1)


        # Tool options 
        self.tool_options_layout = QVBoxLayout()
        self.tool_options_layout.setSpacing(5)

        self.tool_options_container = QWidget()
        self.tool_options_container.setLayout(self.tool_options_layout)
        self.main_layout.addWidget(self.tool_options_container, stretch=2)

        
        # split preview button
        split_preview_button = QPushButton("Split Preview")

        self.main_layout.addWidget(split_preview_button)
        split_preview_button.clicked.connect(self.on_split_preview_click)

        self.tool_list.setCurrentRow(0)
        

    def get(self):
        return self.main_widget

    def on_tool_selected(self, current, previous):
        print("on_tool_selected")
        
        self._clear_layout(self.tool_options_layout)



        if current.text() == "Exposure":
            self._create_exposure_tool()
        elif current.text() == "Brightness and Contrast":
            self._create_brightness_and_contrast_tool()
        elif current.text() == "Colors":
            self._create_colors_tool()
        elif current.text() == "Tones":
            self._create_tones_tool()
        elif current.text() == "Filters":
            self._create_filter_tool()
        elif current.text() == "Crop":
            self._create_crop_tool()
        else:
            self._create_empty_tool()

        self.tool_options_layout.addStretch()

    def on_split_preview_click(self):
        print("on_split_preview_click")
        self.core.toogle_split_preview()

    
    def _create_empty_tool(self):
        label = QLabel("unknown tool")
        self.tool_options_layout.addWidget(label)

    """
        exposure tool
    """
    def _create_exposure_tool(self):
        # exposure options
        ev_min, ev_max, ev_default, ev_curr = self.core.get_ev_state()

        ev_layout = QHBoxLayout()

        # label
        ev_label = QLabel("Exposure " + str(round(ev_curr, 2)))
        self.tool_options_layout.addWidget(ev_label)

        # slider
        ev_slider = QSlider(Qt.Horizontal)
        ev_slider.setRange(int(self.n_steps*ev_min), int(self.n_steps*ev_max))
        ev_slider.setValue(int(self.n_steps*ev_curr))
        ev_layout.addWidget(ev_slider)

        # button
        ev_reset_button = QPushButton("X")
        ev_reset_button.setFixedSize(30, 30)
        ev_layout.addWidget(ev_reset_button)
       
        self.tool_options_layout.addLayout(ev_layout)

        # callbacks
        ev_slider.valueChanged.connect(lambda : self.on_ev_change(ev_slider, ev_label))
        ev_reset_button.clicked.connect(lambda : self.on_ev_reset(ev_slider, ev_label))




        # adaptive exposure options
        ev_adaptive_min, ev_adaptive_max, ev_adaptive_default, ev_adaptive_curr = self.core.get_ev_adaptive_state()

        ev_adaptive_layout = QHBoxLayout()

        # label
        ev_adaptive_label = QLabel("Adaptive Exposure " + str(round(ev_adaptive_curr, 2)))
        self.tool_options_layout.addWidget(ev_adaptive_label)

        # slider
        ev_adaptive_slider = QSlider(Qt.Horizontal)
        ev_adaptive_slider.setRange(int(self.n_steps*ev_adaptive_min), int(self.n_steps*ev_adaptive_max))
        ev_adaptive_slider.setValue(int(self.n_steps*ev_adaptive_curr))
        ev_adaptive_layout.addWidget(ev_adaptive_slider)

        # button
        ev_adaptive_reset_button = QPushButton("X")
        ev_adaptive_reset_button.setFixedSize(30, 30)
        ev_adaptive_layout.addWidget(ev_adaptive_reset_button)
       
        self.tool_options_layout.addLayout(ev_adaptive_layout)

        # callbacks
        ev_adaptive_slider.valueChanged.connect(lambda : self.on_ev_adaptive_change(ev_adaptive_slider, ev_adaptive_label))
        ev_adaptive_reset_button.clicked.connect(lambda : self.on_ev_adaptive_reset(ev_adaptive_slider, ev_adaptive_label))




        #
        # Temperature options
        #
        wb_min, wb_max, wb_default, wb_curr = self.core.get_wb_state()

        wb_layout = QHBoxLayout()

        # label
        wb_label = QLabel("White balance " + str(int(wb_curr)) + "K")
        self.tool_options_layout.addWidget(wb_label)

        # slider
        wb_slider = QSlider(Qt.Horizontal)
        wb_slider.setRange(int(self.n_steps*wb_min), int(self.n_steps*wb_max))
        wb_slider.setValue(int(self.n_steps*wb_curr))
        wb_layout.addWidget(wb_slider)

        # button
        wb_reset_button = QPushButton("X")
        wb_reset_button.setFixedSize(30, 30)
        wb_layout.addWidget(wb_reset_button)
       
        self.tool_options_layout.addLayout(wb_layout)

        # callbacks
        wb_slider.valueChanged.connect(lambda : self.on_wb_change(wb_slider, wb_label))
        wb_reset_button.clicked.connect(lambda : self.on_wb_reset(wb_slider, wb_label))


    def on_ev_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_ev(value)
        label.setText("Exposure " + str(round(value, 2)))
        

    def on_ev_reset(self, slider, label):
        ev_min, ev_max, ev_default, ev_curr = self.core.get_ev_state()
        self.core.set_ev(ev_default)
        label.setText("Exposure " + str(round(ev_default, 2)))
        slider.setValue(int(ev_default*self.n_steps))


    def on_ev_adaptive_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_ev_adaptive(value)
        label.setText("Adaptive Exposure " + str(round(value, 2)))
        

    def on_ev_adaptive_reset(self, slider, label):
        ev_adaptive_min, ev_adaptive_max, ev_adaptive_default, ev_adaptive_curr = self.core.get_ev_adaptive_state()
        self.core.set_ev(ev_adaptive_default)
        label.setText("Adaptive Exposure " + str(round(ev_adaptive_default, 2)))
        slider.setValue(int(ev_adaptive_default*self.n_steps))


    def on_wb_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_wb(value)
        label.setText("White balance " + str(int(value)) + "K")
        

    def on_wb_reset(self, slider, label):
        wb_min, wb_max, wb_default, wb_curr = self.core.get_wb_state()
        self.core.set_wb(wb_default)
        label.setText("White balance " + str(int(wb_curr)) + "K")
        slider.setValue(int(wb_default*self.n_steps))




    """
        brightness and contrast tool
    """
    def _create_brightness_and_contrast_tool(self):
        # brightness options
        brightness_min, brightness_max, brightness_default, brightness_curr = self.core.get_brightness_state()

        brightness_layout = QHBoxLayout()

        # label
        brightness_label = QLabel("Brightness " + str(round(brightness_curr, 2)))
        self.tool_options_layout.addWidget(brightness_label)

        # slider
        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setRange(int(self.n_steps*brightness_min), int(self.n_steps*brightness_max))
        brightness_slider.setValue(int(self.n_steps*brightness_curr))
        brightness_layout.addWidget(brightness_slider)

        # button
        brightness_reset_button = QPushButton("X")
        brightness_reset_button.setFixedSize(30, 30)
        brightness_layout.addWidget(brightness_reset_button)
       
        self.tool_options_layout.addLayout(brightness_layout)

        # callbacks
        brightness_slider.valueChanged.connect(lambda : self.on_brightness_change(brightness_slider, brightness_label))
        brightness_reset_button.clicked.connect(lambda : self.on_brightness_reset(brightness_slider, brightness_label))




        # contrast options
        contrast_min, contrast_max, contrast_default, contrast_curr = self.core.get_contrast_state()

        contrast_layout = QHBoxLayout()

        # label
        contrast_label = QLabel("Contrast " + str(round(contrast_curr, 2)))
        self.tool_options_layout.addWidget(contrast_label)

        # slider
        contrast_slider = QSlider(Qt.Horizontal)
        contrast_slider.setRange(int(self.n_steps*contrast_min), int(self.n_steps*contrast_max))
        contrast_slider.setValue(int(self.n_steps*contrast_curr))
        contrast_layout.addWidget(contrast_slider)

        # button
        contrast_reset_button = QPushButton("X")
        contrast_reset_button.setFixedSize(30, 30)
        contrast_layout.addWidget(contrast_reset_button)
       
        self.tool_options_layout.addLayout(contrast_layout)

        # callbacks
        contrast_slider.valueChanged.connect(lambda : self.on_contrast_change(contrast_slider, contrast_label))
        contrast_reset_button.clicked.connect(lambda : self.on_contrast_reset(contrast_slider, contrast_label))

    def on_brightness_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_brightness(value)
        label.setText("Brightness " + str(round(value, 2)))
        

    def on_brightness_reset(self, slider, label):
        brightness_min, brightness_max, brightness_default, brightness_curr = self.core.get_brightness_state()
        self.core.set_brightness(brightness_default)
        label.setText("Brightness " + str(round(brightness_default, 2)))
        slider.setValue(int(brightness_default*self.n_steps))

    def on_contrast_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_contrast(value)
        label.setText("Contrast " + str(round(value, 2)))
        

    def on_contrast_reset(self, slider, label):
        contrast_min, contrast_max, contrast_default, contrast_curr = self.core.get_contrast_state()
        self.core.set_contrast(contrast_default)
        label.setText("Xontrast " + str(round(contrast_default, 2)))
        slider.setValue(int(contrast_default*self.n_steps))

    
    




    """
        colors tool
    """
    def _create_colors_tool(self):
        # clarity options
        clarity_min, clarity_max, clarity_default, clarity_curr = self.core.get_clarity_state()

        clarity_layout = QHBoxLayout()


        # label
        clarity_label = QLabel("clarity " + str(round(clarity_curr, 2)))
        self.tool_options_layout.addWidget(clarity_label)

        # slider
        clarity_slider = QSlider(Qt.Horizontal)
        clarity_slider.setRange(int(self.n_steps*clarity_min), int(self.n_steps*clarity_max))
        clarity_slider.setValue(int(self.n_steps*clarity_curr))
        clarity_layout.addWidget(clarity_slider)

        # button
        clarity_reset_button = QPushButton("X")
        clarity_reset_button.setFixedSize(30, 30)
        clarity_layout.addWidget(clarity_reset_button)
       
        self.tool_options_layout.addLayout(clarity_layout)

        # callbacks
        clarity_slider.valueChanged.connect(lambda : self.on_clarity_change(clarity_slider, clarity_label))
        clarity_reset_button.clicked.connect(lambda : self.on_clarity_reset(clarity_slider, clarity_label))



        # saturation options
        saturation_min, saturation_max, saturation_default, saturation_curr = self.core.get_saturation_state()

        saturation_layout = QHBoxLayout()


        # label
        saturation_label = QLabel("Saturation " + str(round(saturation_curr, 2)))
        self.tool_options_layout.addWidget(saturation_label)

        # slider
        saturation_slider = QSlider(Qt.Horizontal)
        saturation_slider.setRange(int(self.n_steps*saturation_min), int(self.n_steps*saturation_max))
        saturation_slider.setValue(int(self.n_steps*saturation_curr))
        saturation_layout.addWidget(saturation_slider)

        # button
        saturation_reset_button = QPushButton("X")
        saturation_reset_button.setFixedSize(30, 30)
        saturation_layout.addWidget(saturation_reset_button)
       
        self.tool_options_layout.addLayout(saturation_layout)

        # callbacks
        saturation_slider.valueChanged.connect(lambda : self.on_saturation_change(saturation_slider, saturation_label))
        saturation_reset_button.clicked.connect(lambda : self.on_saturation_reset(saturation_slider, saturation_label))



        # vibrance options
        vibrance_min, vibrance_max, vibrance_default, vibrance_curr = self.core.get_vibrance_state()

        vibrance_layout = QHBoxLayout()

        # label
        vibrance_label = QLabel("Vibrance " + str(round(vibrance_curr, 2)))
        self.tool_options_layout.addWidget(vibrance_label)

        # slider
        vibrance_slider = QSlider(Qt.Horizontal)
        vibrance_slider.setRange(int(self.n_steps*vibrance_min), int(self.n_steps*vibrance_max))
        vibrance_slider.setValue(int(self.n_steps*vibrance_curr))
        vibrance_layout.addWidget(vibrance_slider)

        # button
        vibrance_reset_button = QPushButton("X")
        vibrance_reset_button.setFixedSize(30, 30)
        vibrance_layout.addWidget(vibrance_reset_button)
       
        self.tool_options_layout.addLayout(vibrance_layout)

        # callbacks
        vibrance_slider.valueChanged.connect(lambda : self.on_vibrance_change(vibrance_slider, vibrance_label))
        vibrance_reset_button.clicked.connect(lambda : self.on_vibrance_reset(vibrance_slider, vibrance_label))



        # equalisation options
        equalisation_min, equalisation_max, equalisation_default, equalisation_curr = self.core.get_equalisation_state()

        equalisation_layout = QHBoxLayout()

        # label
        equalisation_label = QLabel("Equalisation " + str(round(equalisation_curr, 2)))
        self.tool_options_layout.addWidget(equalisation_label)

        # slider
        equalisation_slider = QSlider(Qt.Horizontal)
        equalisation_slider.setRange(int(self.n_steps*equalisation_min), int(self.n_steps*equalisation_max))
        equalisation_slider.setValue(int(self.n_steps*equalisation_curr))
        equalisation_layout.addWidget(equalisation_slider)

        # button
        equalisation_reset_button = QPushButton("X")
        equalisation_reset_button.setFixedSize(30, 30)
        equalisation_layout.addWidget(equalisation_reset_button)
       
        self.tool_options_layout.addLayout(equalisation_layout)

        # callbacks 
        equalisation_slider.valueChanged.connect(lambda : self.on_equalisation_change(equalisation_slider, equalisation_label))
        equalisation_reset_button.clicked.connect(lambda : self.on_equalisation_reset(equalisation_slider, equalisation_label))

    def on_clarity_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_clarity(value)
        label.setText("Clarity " + str(round(value, 2)))
        

    def on_clarity_reset(self, slider, label):
        clarity_min, clarity_max, clarity_default, clarity_curr = self.core.get_clarity_state()
        self.core.set_clarity(clarity_default)
        label.setText("Clarity " + str(round(clarity_default, 2)))
        slider.setValue(int(clarity_default*self.n_steps))


    def on_saturation_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_saturation(value)
        label.setText("Saturation " + str(round(value, 2)))
        

    def on_saturation_reset(self, slider, label):
        saturation_min, saturation_max, saturation_default, saturation_curr = self.core.get_saturation_state()
        self.core.set_saturation(saturation_default)
        label.setText("Saturation " + str(round(saturation_default, 2)))
        slider.setValue(int(saturation_default*self.n_steps))

    def on_vibrance_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_vibrance(value)
        label.setText("Vibrance " + str(round(value, 2)))
        

    def on_vibrance_reset(self, slider, label):
        vibrance_min, vibrance_max, vibrance_default, vibrance_curr = self.core.get_vibrance_state()
        self.core.set_vibrance(vibrance_default)
        label.setText("Vibrance " + str(round(vibrance_default, 2)))
        slider.setValue(int(vibrance_default*self.n_steps))

    def on_equalisation_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_equalisation(value)
        label.setText("equalisation " + str(round(value, 2)))
        

    def on_equalisation_reset(self, slider, label):
        equalisation_min, equalisation_max, equalisation_default, equalisation_curr = self.core.get_equalisation_state()
        self.core.set_equalisation(equalisation_default)
        label.setText("Equalisation " + str(round(equalisation_default, 2)))
        slider.setValue(int(equalisation_default*self.n_steps))

    



    """
        tones tool
    """
    def _create_tones_tool(self):
        # tones options
        tones_min, tones_max, tones_default, tones_dark_curr, tones_mid_curr, tones_high_curr = self.core.get_tones_state()

        
        # dark tones - shadows
        tones_dark_layout = QHBoxLayout()

        # label
        tones_dark_label = QLabel("Shadows " + str(round(tones_dark_curr, 2)))
        self.tool_options_layout.addWidget(tones_dark_label)

        # slider
        tones_dark_slider = QSlider(Qt.Horizontal)
        tones_dark_slider.setRange(int(self.n_steps*tones_min), int(self.n_steps*tones_max))
        tones_dark_slider.setValue(int(self.n_steps*tones_dark_curr))
        tones_dark_layout.addWidget(tones_dark_slider)

        # button
        tones_dark_reset_button = QPushButton("X")
        tones_dark_reset_button.setFixedSize(30, 30)
        tones_dark_layout.addWidget(tones_dark_reset_button)
       
        self.tool_options_layout.addLayout(tones_dark_layout)

        # callbacks
        tones_dark_slider.valueChanged.connect(lambda : self.on_tones_dark_change(tones_dark_slider, tones_dark_label))
        tones_dark_reset_button.clicked.connect(lambda : self.on_tones_dark_reset(tones_dark_slider, tones_dark_label))



        # mid tones
        tones_mid_layout = QHBoxLayout()

        # label
        tones_mid_label = QLabel("Midtones " + str(round(tones_mid_curr, 2)))
        self.tool_options_layout.addWidget(tones_mid_label)

        # slider
        tones_mid_slider = QSlider(Qt.Horizontal)   
        tones_mid_slider.setRange(int(self.n_steps*tones_min), int(self.n_steps*tones_max))
        tones_mid_slider.setValue(int(self.n_steps*tones_mid_curr))
        tones_mid_layout.addWidget(tones_mid_slider)

        # button
        tones_mid_reset_button = QPushButton("X")
        tones_mid_reset_button.setFixedSize(30, 30)
        tones_mid_layout.addWidget(tones_mid_reset_button)
       
        self.tool_options_layout.addLayout(tones_mid_layout)

        # callbacks
        tones_mid_slider.valueChanged.connect(lambda : self.on_tones_mid_change(tones_mid_slider, tones_mid_label))
        tones_mid_reset_button.clicked.connect(lambda : self.on_tones_mid_reset(tones_mid_slider, tones_mid_label))



        # high tones - highlights
        tones_high_layout = QHBoxLayout()

        # label
        tones_high_label = QLabel("Highlights " + str(round(tones_high_curr, 2)))
        self.tool_options_layout.addWidget(tones_high_label)

        # slider
        tones_high_slider = QSlider(Qt.Horizontal)   
        tones_high_slider.setRange(int(self.n_steps*tones_min), int(self.n_steps*tones_max))
        tones_high_slider.setValue(int(self.n_steps*tones_high_curr))
        tones_high_layout.addWidget(tones_high_slider)

        # button
        tones_high_reset_button = QPushButton("X")
        tones_high_reset_button.setFixedSize(30, 30)
        tones_high_layout.addWidget(tones_high_reset_button)
       
        self.tool_options_layout.addLayout(tones_high_layout)

        # callbacks 
        tones_high_slider.valueChanged.connect(lambda : self.on_tones_high_change(tones_high_slider, tones_high_label))
        tones_high_reset_button.clicked.connect(lambda : self.on_tones_high_reset(tones_high_slider, tones_high_label))
        


        #colors options
        colors_min, colors_max, colors_default, colors_red_curr, colors_green_curr, colors_blue_curr = self.core.get_colors_state()


        # red color
        red_color_layout = QHBoxLayout()

        # label
        red_color_label = QLabel("Red " + str(round(colors_red_curr, 2)))
        self.tool_options_layout.addWidget(red_color_label)

        # slider
        red_color_slider = QSlider(Qt.Horizontal)   
        red_color_slider.setRange(int(self.n_steps*colors_min), int(self.n_steps*colors_max))
        red_color_slider.setValue(int(self.n_steps*colors_red_curr))
        red_color_layout.addWidget(red_color_slider)

        # button
        red_color_reset_button = QPushButton("X")
        red_color_reset_button.setFixedSize(30, 30)
        red_color_layout.addWidget(red_color_reset_button)
       
        self.tool_options_layout.addLayout(red_color_layout)

        # callbacks 
        red_color_slider.valueChanged.connect(lambda : self.on_red_color_change(red_color_slider, red_color_label))
        red_color_reset_button.clicked.connect(lambda : self.on_red_color_reset(red_color_slider, red_color_label))



        # green color
        green_color_layout = QHBoxLayout()

        # label
        green_color_label = QLabel("Green " + str(round(colors_green_curr, 2)))
        self.tool_options_layout.addWidget(green_color_label)

        # slider
        green_color_slider = QSlider(Qt.Horizontal)   
        green_color_slider.setRange(int(self.n_steps*colors_min), int(self.n_steps*colors_max))
        green_color_slider.setValue(int(self.n_steps*colors_green_curr))
        green_color_layout.addWidget(green_color_slider)

        # button
        green_color_reset_button = QPushButton("X")
        green_color_reset_button.setFixedSize(30, 30)
        green_color_layout.addWidget(green_color_reset_button)
       
        self.tool_options_layout.addLayout(green_color_layout)

        # callbacks 
        green_color_slider.valueChanged.connect(lambda : self.on_green_color_change(green_color_slider, green_color_label))
        green_color_reset_button.clicked.connect(lambda : self.on_green_color_reset(green_color_slider, green_color_label))



        # blue color
        blue_color_layout = QHBoxLayout()

        # label
        blue_color_label = QLabel("Blue " + str(round(colors_blue_curr, 2)))
        self.tool_options_layout.addWidget(blue_color_label)

        # slider
        blue_color_slider = QSlider(Qt.Horizontal)   
        blue_color_slider.setRange(int(self.n_steps*colors_min), int(self.n_steps*colors_max))
        blue_color_slider.setValue(int(self.n_steps*colors_blue_curr))
        blue_color_layout.addWidget(blue_color_slider)

        # button
        blue_color_reset_button = QPushButton("X")
        blue_color_reset_button.setFixedSize(30, 30)
        blue_color_layout.addWidget(blue_color_reset_button)
       
        self.tool_options_layout.addLayout(blue_color_layout)

        # callbacks 
        blue_color_slider.valueChanged.connect(lambda : self.on_blue_color_change(blue_color_slider, blue_color_label))
        blue_color_reset_button.clicked.connect(lambda : self.on_blue_color_reset(blue_color_slider, blue_color_label))






    def on_tones_dark_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_dark(value)
        label.setText("Shadows " + str(round(value, 2)))
        

    def on_tones_dark_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_dark_curr, tones_mid_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_dark(tones_default)
        slider.setValue(int(tones_default*self.n_steps))


    def on_tones_mid_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_mid(value)
        label.setText("Midtones " + str(round(value, 2)))
        

    def on_tones_mid_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_mid_curr, tones_mid_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_mid(tones_default)
        slider.setValue(int(tones_default*self.n_steps))

    
    def on_tones_high_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_high(value)
        label.setText("Highlights " + str(round(value, 2)))
        

    def on_tones_high_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_high_curr, tones_high_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_mid(tones_default)
        slider.setValue(int(tones_default*self.n_steps))

    

    def on_red_color_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_colors_red(value)
        label.setText("Red " + str(round(value, 2)))
    
    def on_red_color_reset(self, slider, value):
        colors_min, colors_max, colors_default, colors_red_curr, colors_green_curr, colors_blue_curr = self.core.get_colors_state()
        self.core.set_colors_red(colors_default)
        slider.setValue(int(colors_default*self.n_steps))

    def on_green_color_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_colors_green(value)
        label.setText("Green " + str(round(value, 2)))
    
    def on_green_color_reset(self, slider, value):
        colors_min, colors_max, colors_default, colors_red_curr, colors_green_curr, colors_blue_curr = self.core.get_colors_state()
        self.core.set_colors_green(colors_default)
        slider.setValue(int(colors_default*self.n_steps))

    def on_blue_color_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_colors_blue(value)
        label.setText("Blue " + str(round(value, 2)))
    
    def on_blue_color_reset(self, slider, value):
        colors_min, colors_max, colors_default, colors_red_curr, colors_green_curr, colors_blue_curr = self.core.get_colors_state()
        self.core.set_colors_blue(colors_default)
        slider.setValue(int(colors_default*self.n_steps))



    """
        filter tool
    """
    def _create_filter_tool(self):
        # blur options
        blur_min, blur_max, blur_default, blur_curr = self.core.get_blur_state()

        blur_layout = QHBoxLayout()

        # label
        blur_label = QLabel("Gaussian Blur " + str(round(blur_curr, 2)))
        self.tool_options_layout.addWidget(blur_label)

        # slider
        blur_slider = QSlider(Qt.Horizontal)
        blur_slider.setRange(int(self.n_steps*blur_min), int(self.n_steps*blur_max))
        blur_slider.setValue(int(self.n_steps*blur_curr))
        blur_layout.addWidget(blur_slider)

        # button
        blur_reset_button = QPushButton("X")
        blur_reset_button.setFixedSize(30, 30)
        blur_layout.addWidget(blur_reset_button)
       
        self.tool_options_layout.addLayout(blur_layout)

        # callbacks
        blur_slider.valueChanged.connect(lambda : self.on_blur_change(blur_slider, blur_label))
        blur_reset_button.clicked.connect(lambda : self.on_blur_reset(blur_slider, blur_label))



        # sharpen options
        sharpen_min, sharpen_max, sharpen_default, sharpen_curr = self.core.get_sharpen_state()

        sharpen_layout = QHBoxLayout()

        # label
        sharpen_label = QLabel("Sharpen " + str(round(sharpen_curr, 2)))
        self.tool_options_layout.addWidget(sharpen_label)

        # slider
        sharpen_slider = QSlider(Qt.Horizontal)
        sharpen_slider.setRange(int(self.n_steps*sharpen_min), int(self.n_steps*sharpen_max))
        sharpen_slider.setValue(int(self.n_steps*sharpen_curr))
        sharpen_layout.addWidget(sharpen_slider)

        # button
        sharpen_reset_button = QPushButton("X")
        sharpen_reset_button.setFixedSize(30, 30)
        sharpen_layout.addWidget(sharpen_reset_button)
       
        self.tool_options_layout.addLayout(sharpen_layout)

        # callbacks
        sharpen_slider.valueChanged.connect(lambda : self.on_sharpen_change(sharpen_slider, sharpen_label))
        sharpen_reset_button.clicked.connect(lambda : self.on_sharpen_reset(sharpen_slider, sharpen_label))



        # bilateral options
        bilateral_min, bilateral_max, bilateral_default, bilateral_curr = self.core.get_bilateral_state()

        bilateral_layout = QHBoxLayout()

        # label
        bilateral_label = QLabel("bilateral " + str(round(bilateral_curr, 2)))
        self.tool_options_layout.addWidget(bilateral_label)

        # slider
        bilateral_slider = QSlider(Qt.Horizontal)
        bilateral_slider.setRange(int(self.n_steps*bilateral_min), int(self.n_steps*bilateral_max))
        bilateral_slider.setValue(int(self.n_steps*bilateral_curr))
        bilateral_layout.addWidget(bilateral_slider)

        # button
        bilateral_reset_button = QPushButton("X")
        bilateral_reset_button.setFixedSize(30, 30)
        bilateral_layout.addWidget(bilateral_reset_button)
       
        self.tool_options_layout.addLayout(bilateral_layout)

        # callbacks 
        bilateral_slider.valueChanged.connect(lambda : self.on_bilateral_change(bilateral_slider, bilateral_label))
        bilateral_reset_button.clicked.connect(lambda : self.on_bilateral_reset(bilateral_slider, bilateral_label))

    def on_blur_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_blur(value)
        label.setText("Gaussian Blur " + str(round(value, 2)))
        

    def on_blur_reset(self, slider, label):
        blur_min, blur_max, blur_default, blur_curr = self.core.get_blur_state()
        self.core.set_blur(blur_default)
        slider.setValue(int(blur_default*self.n_steps))

    def on_sharpen_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_sharpen(value)
        label.setText("Sharpen " + str(round(value, 2)))
        

    def on_sharpen_reset(self, slider, label):
        sharpen_min, sharpen_max, sharpen_default, sharpen_curr = self.core.get_sharpen_state()
        self.core.set_sharpen(sharpen_default)
        slider.setValue(int(sharpen_default*self.n_steps))

    def on_bilateral_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_bilateral(value)
        label.setText("Bilateral " + str(round(value, 2)))
        

    def on_bilateral_reset(self, slider, label):
        bilateral_min, bilateral_max, bilateral_default, bilateral_curr = self.core.get_bilateral_state()
        self.core.set_bilateral(bilateral_default)
        slider.setValue(int(bilateral_default*self.n_steps))


    
    
    
    





    """
        image crop tool
    """
    def _create_crop_tool(self):
        
        crop_modes, crop_default, crop_curr = self.core.get_crop_state()

        self.tool_options_layout.addWidget(QLabel("Cropping Options"))

        aspect_ratio_list = QListWidget()

        aspect_ratio_list.addItems(crop_modes)
        font = QFont()
        font.setPointSize(16)
        aspect_ratio_list.setFont(font)

        aspect_ratio_list.currentItemChanged.connect(self.on_aspect_ratio_selected)   
        self.tool_options_layout.addWidget(aspect_ratio_list)

        aspect_ratio_list.setCurrentRow(crop_curr)
        
    def on_aspect_ratio_selected(self, current, previous):
        mode_name = current.text()
        crop_modes, crop_default, crop_curr = self.core.get_crop_state()

        for i in range(len(crop_modes)):
            if mode_name == crop_modes[i]:
                self.core.set_crop_mode(i)
                break   


    def update_histogram(self, histogram):       
        all     = histogram[0]
        red     = histogram[1]
        green   = histogram[2]
        blue    = histogram[3]

        self.histogram_widget.clear()
        self.histogram_widget.plot(all, pen=pg.mkPen("w"))
        self.histogram_widget.plot(red, pen=pg.mkPen("r"))
        self.histogram_widget.plot(green, pen=pg.mkPen("g"))
        self.histogram_widget.plot(blue, pen=pg.mkPen("b"))


    def _clear_layout(self, layout):
        while layout.count():  # Loop until no items are left in the layout
            item = layout.takeAt(0)  # Take the first item
        
            # Check if the item is a widget
            if widget := item.widget():
                widget.deleteLater()  # Delete the widget
        
            # Check if the item is a layout
            elif sub_layout := item.layout():
                self._clear_layout(sub_layout)  # Recursively clear the sub-layout

            else:
                print("_clear_layout unknown item ", item)

            del item

   
