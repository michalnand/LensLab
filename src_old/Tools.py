from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QListWidget,
                             QSlider, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg

import sys
import numpy

class Core:

    def __init__(self):
        
        self.tool_names = []
        self.tool_names.append("Exposure")
        self.tool_names.append("Brightness and Contrast")
        self.tool_names.append("Colors")
        self.tool_names.append("Tones")
        self.tool_names.append("Filters")
        self.tool_names.append("Crop")


        self.ev_min     = -4.0
        self.ev_max     = 4.0
        self.ev_default = 0.0
        self.ev_curr    = self.ev_default


        self.wb_min     = 2000.0
        self.wb_max     = 20000.0
        self.wb_default = 6500.0
        self.wb_curr    = self.wb_default


        self.brightness_min     = -1.0
        self.brightness_max     = 1.0
        self.brightness_default = 0.0
        self.brightness_curr    = self.brightness_default

        
        self.contrast_min       = 0.0
        self.contrast_max       = 5.0
        self.contrast_default   = 1.0
        self.contrast_curr      = self.contrast_default


        self.saturation_min       = 0.0
        self.saturation_max       = 4.0
        self.saturation_default   = 1.0
        self.saturation_curr      = self.saturation_default

        self.vibrance_min       = 0.0
        self.vibrance_max       = 4.0
        self.vibrance_default   = 1.0
        self.vibrance_curr      = self.vibrance_default

        self.equalisation_min       = 0.0   
        self.equalisation_max       = 1.0
        self.equalisation_default   = 0.0
        self.equalisation_curr      = self.equalisation_default


        self.blur_min         = 0.0
        self.blur_max         = 1.0
        self.blur_default     = 0.0
        self.blur_curr        = self.blur_default


        
        self.tones_min          = -0.1
        self.tones_max          = 0.1
        self.tones_default      = 0.0
        self.tones_dark_curr    = self.tones_default
        self.tones_mid_curr     = self.tones_default
        self.tones_high_curr    = self.tones_default


        
        self.sharpen_min         = 0.0
        self.sharpen_max         = 1.0
        self.sharpen_default     = 0.0
        self.sharpen_curr        = self.sharpen_default

        
        self.bilateral_min         = 0.0
        self.bilateral_max         = 1.0
        self.bilateral_default     = 0.0
        self.bilateral_curr        = self.bilateral_default


        self.crop_modes     = ["Original image", "Free hand", "16:9", "4:3", "3:2", "1:1", "9:16", "3:4", "2:3", "1.85:1", "2.35:1", "16:10"]
        self.crop_ratio_x   = [-1,   -1, 16, 4, 3, 1,  9, 3, 2, 1.85, 2.35, 16]
        self.crop_ratio_y   = [-1,   -1,  9, 3, 2, 1, 16, 4, 3,    1,    1, 10]

        self.crop_default   = 0
        self.crop_curr      = 0


    def get_tool_names(self):
        return self.tool_names
    
    def get_histogram(self):
        return numpy.random.rand(4, 256)
    
    
    def get_ev_state(self):
        return self.ev_min, self.ev_max, self.ev_default, self.ev_curr

    def set_ev(self, value):
        self.ev_curr = value


    def get_wb_state(self):
        return self.wb_min, self.wb_max, self.wb_default, self.wb_curr

    def set_wb(self, value):
        self.wb_curr = value



    def get_brightness_state(self):
        return self.brightness_min, self.brightness_max, self.brightness_default, self.brightness_curr
 
    def set_brightness(self, value):
        self.brightness_curr = value

    def get_contrast_state(self):
        return self.contrast_min, self.contrast_max, self.contrast_default, self.contrast_curr
 
    def set_contrast(self, value):
        self.contrast_curr = value


    def get_saturation_state(self):
        return self.saturation_min, self.saturation_max, self.saturation_default, self.saturation_curr
 
    def set_saturation(self, value):
        self.saturation_curr = value


    def get_vibrance_state(self):
        return self.vibrance_min, self.vibrance_max, self.vibrance_default, self.vibrance_curr
 
    def set_vibrance(self, value):
        self.vibrance_curr = value


    def get_equalisation_state(self):
        return self.equalisation_min, self.equalisation_max, self.equalisation_default, self.equalisation_curr
 
    def set_equalisation(self, value):
        self.equalisation_curr = value


    def get_tones_state(self):
        return self.tones_min, self.tones_max, self.tones_default, self.tones_dark_curr, self.tones_mid_curr, self.tones_high_curr
 
    def set_tones_dark(self, value):
        self.tones_dark_curr = value

    def set_tones_mid(self, value):
        self.tones_mid_curr = value

    def set_tones_high(self, value):
        self.tones_high_curr = value



    def get_blur_state(self):
        return self.blur_min, self.blur_max, self.blur_default, self.blur_curr
 
    def set_blur(self, value):
        self.blur_curr = value

    def get_sharpen_state(self):
        return self.sharpen_min, self.sharpen_max, self.sharpen_default, self.sharpen_curr
 
    def set_sharpen(self, value):
        self.sharpen_curr = value

    def get_bilateral_state(self):
        return self.bilateral_min, self.bilateral_max, self.bilateral_default, self.bilateral_curr
 
    def set_bilateral(self, value):
        self.bilateral_curr = value


    def get_crop_state(self):
        return self.crop_modes, self.crop_default, self.crop_curr
    
    def set_crop_mode(self, value):
        self.crop_curr = value
        print("crop set to ", self.crop_curr)

    def update_small(self):
        print("apply settings : update_small")
    
class Tools(QWidget):
    def __init__(self, core):
        super().__init__()

        self.n_steps = 64
        self.core = core

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
        self.tool_options_container = QWidget()
        self.tool_options_container.setLayout(self.tool_options_layout)
        self.main_layout.addWidget(self.tool_options_container, stretch=2)


        # split preview button
        split_preview_button = QPushButton("Split Preview")

        self.main_layout.addWidget(split_preview_button)
        split_preview_button.clicked.connect(self.on_split_preview_click)

        
        self.tool_list.setCurrentRow(0)
        #self._clear_layout(self.tool_options_layout)
        #self._create_exposure_tool()

    def get(self):
        return self.main_widget

    def on_tool_selected(self, current, previous):
        print("on_tool_selected")
        
        self._clear_layout(self.tool_options_layout)

        self._update_histogram()

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

    def on_split_preview_click(self):
        pass

    
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
        
        self.core.update_small()
        self._update_histogram()

    def on_ev_reset(self, slider, label):
        ev_min, ev_max, ev_default, ev_curr = self.core.get_ev_state()
        self.core.set_ev(ev_default)
        label.setText("Exposure " + str(round(ev_default, 2)))
        slider.setValue(int(ev_default*self.n_steps))

    def on_wb_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_wb(value)
        label.setText("White balance " + str(int(value)) + "K")
        
        self.core.update_small()
        self._update_histogram()

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
        
        self.core.update_small()
        self._update_histogram()

    def on_brightness_reset(self, slider, label):
        brightness_min, brightness_max, brightness_default, brightness_curr = self.core.get_brightness_state()
        self.core.set_brightness(brightness_default)
        label.setText("Brightness " + str(round(brightness_default, 2)))
        slider.setValue(int(brightness_default*self.n_steps))

    def on_contrast_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_contrast(value)
        label.setText("Contrast " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_contrast_reset(self, slider, label):
        contrast_min, contrast_max, contrast_default, contrast_curr = self.core.get_contrast_state()
        self.core.set_contrast(contrast_default)
        label.setText("Xontrast " + str(round(contrast_default, 2)))
        slider.setValue(int(contrast_default*self.n_steps))

    
    




    """
        colors tool
    """
    def _create_colors_tool(self):
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

    def on_saturation_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_saturation(value)
        label.setText("Saturation " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_saturation_reset(self, slider, label):
        saturation_min, saturation_max, saturation_default, saturation_curr = self.core.get_saturation_state()
        self.core.set_saturation(saturation_default)
        label.setText("Saturation " + str(round(saturation_default, 2)))
        slider.setValue(int(saturation_default*self.n_steps))

    def on_vibrance_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_vibrance(value)
        label.setText("Vibrance " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_vibrance_reset(self, slider, label):
        vibrance_min, vibrance_max, vibrance_default, vibrance_curr = self.core.get_vibrance_state()
        self.core.set_vibrance(vibrance_default)
        label.setText("Vibrance " + str(round(vibrance_default, 2)))
        slider.setValue(int(vibrance_default*self.n_steps))

    def on_equalisation_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_equalisation(value)
        label.setText("equalisation " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

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
        tones_high_label = QLabel("Midtones " + str(round(tones_high_curr, 2)))
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





    def on_tones_dark_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_dark(value)
        label.setText("Shadows " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_tones_dark_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_dark_curr, tones_mid_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_dark(tones_default)
        slider.setValue(int(tones_default*self.n_steps))


    def on_tones_mid_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_mid(value)
        label.setText("Midtones " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_tones_mid_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_mid_curr, tones_mid_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_mid(tones_default)
        slider.setValue(int(tones_default*self.n_steps))

    
    def on_tones_high_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_tones_high(value)
        label.setText("Highlights " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_tones_high_reset(self, slider, label):
        tones_min, tones_max, tones_default, tones_high_curr, tones_high_curr, tones_high_curr = self.core.get_tones_state()

        self.core.set_tones_mid(tones_default)
        slider.setValue(int(tones_default*self.n_steps))

    



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
        
        self.core.update_small()
        self._update_histogram()

    def on_blur_reset(self, slider, label):
        blur_min, blur_max, blur_default, blur_curr = self.core.get_blur_state()
        self.core.set_blur(blur_default)
        slider.setValue(int(blur_default*self.n_steps))

    def on_sharpen_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_sharpen(value)
        label.setText("Sharpen " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

    def on_sharpen_reset(self, slider, label):
        sharpen_min, sharpen_max, sharpen_default, sharpen_curr = self.core.get_sharpen_state()
        self.core.set_sharpen(sharpen_default)
        slider.setValue(int(sharpen_default*self.n_steps))

    def on_bilateral_change(self, slider, label):
        value = slider.value()/self.n_steps
        self.core.set_bilateral(value)
        label.setText("Bilateral " + str(round(value, 2)))
        
        self.core.update_small()
        self._update_histogram()

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


    def _update_histogram(self):
        histogram = self.core.get_histogram()
       
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

   


class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("App Test")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.core   = Core()
        self.tool_widget = Tools(self.core)

        self.main_layout.addWidget(self.tool_widget.get())

        
        self.main_layout.addStretch()


       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main = TestApp()
    app_main.show()
    sys.exit(app.exec_())

